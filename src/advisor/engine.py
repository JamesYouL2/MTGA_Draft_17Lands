"""
src/advisor/engine.py
Scores the cards in a pack for the cards already taken.

A card's score is BASE_SCORE plus a weighted sum of a few named features
(DraftAdvisor.pick_features). The weights come from a conditional logit fitted
to strong 17Lands drafters' picks with Tools/PickFit. They are in points, where
one standard deviation of GIH WR is worth 15, and a point is
PICK_LOG_ODDS_PER_POINT of log-odds that a strong drafter takes the card.
"""

import logging
import re

import numpy as np

from src import constants
from src.advisor.schema import Recommendation
from src.utils import normalize_color_string

logger = logging.getLogger(__name__)

BASE_SCORE = 50.0
SHARE_BINS = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 40), (40, 1000)]
# 17lands counts a deck as splashing a color with 1-3 cards in it, else main.
COUNT_BINS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 9), (9, 1000)]
WEIGHTS = {
    # GIH WR over all decks, in standard deviations of the set's GIH WR.
    "quality": 15.0,
    # GIH WR in the pool's two main colors minus over all decks, in standard
    # deviations, shrunk toward 0 when the pair has few games.
    "lane": 11.1,
    # The pool's strength in the card's colors, in pool cards (see
    # DraftAdvisor.color_strength); a two-color card counts both colors.
    "color_support": 0.9,
    # How far the card's colors are behind the pool's second color, in pool
    # cards.
    "color_gap": -2.0,
    # No GIH WR yet; quality is then 0.
    "unrated": -10.9,
    # Colored mana symbols the pool's two main colors can't pay.
    "off_pips": 0.0,
    # Each of those symbols' color gap (see color_gap), summed.
    "pip_gap": 0.0,
    # Colored mana symbols in the card's cost, by the pool's share of colored
    # mana symbols in that color (see DraftAdvisor.pip_share): "pshare_lo_hi"
    # counts the symbols whose color has lo% to under hi% of the pool's.
    **{f"pshare_{lo}_{hi}": 0.0 for lo, hi in SHARE_BINS},
    # The same by the percentage of the pool's nonland cards in that color.
    **{f"cshare_{lo}_{hi}": 0.0 for lo, hi in SHARE_BINS},
    # The same by the number of the pool's nonland cards in that color.
    **{f"count_{lo}_{hi}": 0.0 for lo, hi in COUNT_BINS},
    # Lane and off_pips against 17lands' color groups instead of the pool's two
    # main colors: "lane_soft_K"/"off_soft_K" average them over the groups,
    # weighted by P(group | pool) (see DraftAdvisor._group_posterior);
    # "lane_map_K"/"off_map_K" use the most likely group, once the pool has two
    # colors.
    **{
        f"{f}_{m}_{k}": 0.0
        for k in ["k025", "k05", "k1", "k2", "k4"]
        for m in ["soft", "map"]
        for f in ["lane", "off"]
    },
}
GROUP_KS = {"k025": 0.25, "k05": 0.5, "k1": 1.0, "k2": 2.0, "k4": 4.0}
PICK_LOG_ODDS_PER_POINT = 0.1023
# A pair's GIH WR from n games counts n / (n + LANE_PRIOR_GAMES) of its
# difference from the all-decks rate.
LANE_PRIOR_GAMES = 2000.0


class DraftAdvisor:
    BOMB_Z_SCORE = 1.5

    def __init__(self, set_metrics, taken_cards: list[dict]):
        self.metrics = set_metrics
        self.pool = taken_cards or []

        self.global_mean, self.global_std = self.metrics.get_metrics(
            "All Decks", "gihwr"
        )
        if self.global_mean <= 0:
            self.global_mean = 54.0
        if self.global_std <= 0:
            self.global_std = 4.0

        self.color_strength = self._color_strength()
        self.pip_share = self._pip_share()
        self.card_count = {c: 0 for c in constants.CARD_COLORS}
        nonland = [c for c in self.pool if "Land" not in c.get("types", [])]
        for card in nonland:
            for c in card.get("colors", []):
                if c in self.card_count:
                    self.card_count[c] += 1
        self.card_share = {
            c: 100.0 * n / len(nonland) if nonland else 0.0
            for c, n in self.card_count.items()
        }
        ranked = sorted(constants.CARD_COLORS, key=lambda c: -self.color_strength[c])
        self.main_colors = [c for c in ranked[:2] if self.color_strength[c] > 0]
        self.second_strength = self.color_strength[ranked[1]]
        self.main_archetype = (
            normalize_color_string("".join(self.main_colors))
            if len(self.main_colors) == 2
            else "All Decks"
        )
        self._groups()

    def _quality(self, card: dict) -> float | None:
        """GIH WR over all decks in standard deviations, or None if unrated."""
        stats = card.get("deck_colors", {}).get("All Decks", {})
        wr = float(stats.get("gihwr") or 0.0)
        if wr <= 0:
            return None
        return (wr - self.global_mean) / self.global_std

    def _color_strength(self) -> dict[str, float]:
        """For each color, the pool's nonland cards of that color, each counted
        as 1 + its quality, so an average card is 1, a bomb more and a card
        a standard deviation below average or worse 0."""
        strength = {c: 0.0 for c in constants.CARD_COLORS}
        for card in self.pool:
            if "Land" in card.get("types", []):
                continue
            weight = max(0.0, 1.0 + (self._quality(card) or 0.0))
            for color in card.get("colors", []):
                if color in strength:
                    strength[color] += weight
        return strength

    @staticmethod
    def _pips(card: dict) -> list[list[str]]:
        """The colors of each colored mana symbol in the card's (front face's)
        cost; empty for hybrid, {2/W} and Phyrexian symbols that need no color."""
        cost = str(card.get("mana_cost") or "").split(" // ")[0]
        pips = []
        for symbol in re.findall(r"\{(.*?)\}", cost):
            options = symbol.split("/")
            colors = [o for o in options if o in constants.CARD_COLORS]
            if colors and not any(o.isdigit() or o == "P" for o in options):
                pips.append(colors)
        return pips

    def _pip_share(self) -> dict[str, float]:
        """For each color, its percentage of the colored mana symbols in the
        pool's nonland cards (a hybrid symbol split between its colors); all 0
        for a pool with none."""
        count = {c: 0.0 for c in constants.CARD_COLORS}
        for card in self.pool:
            if "Land" in card.get("types", []):
                continue
            for colors in self._pips(card):
                for c in colors:
                    count[c] += 1.0 / len(colors)
        total = sum(count.values())
        return {c: 100.0 * n / total if total else 0.0 for c, n in count.items()}

    def _share_bins(self, card: dict) -> dict[str, float]:
        """The card's colored mana symbols counted by bins of the pool's pip
        share, card share and card count in their color (the larger, for a
        hybrid symbol)."""
        out = {}
        for prefix, measure, bins in [
            ("pshare", self.pip_share, SHARE_BINS),
            ("cshare", self.card_share, SHARE_BINS),
            ("count", self.card_count, COUNT_BINS),
        ]:
            out |= {f"{prefix}_{lo}_{hi}": 0.0 for lo, hi in bins}
            for colors in self._pips(card):
                value = max(measure[c] for c in colors)
                for lo, hi in bins:
                    if lo <= value < hi:
                        out[f"{prefix}_{lo}_{hi}"] += 1.0
        return out

    def pick_features(self, card: dict) -> dict[str, float] | None:
        """The card's features for this pool, or None for a basic land."""
        name = str(card.get("name", "")).strip()
        types = card.get("types", [])
        if name in constants.BASIC_LANDS or ("Basic" in types and "Land" in types):
            return None

        quality = self._quality(card)
        lane = 0.0
        if quality is not None and self.main_archetype != "All Decks":
            stats = card.get("deck_colors", {})
            pair = stats.get(self.main_archetype, {})
            pair_wr = float(pair.get("gihwr") or 0.0)
            if pair_wr > 0:
                games = float(pair.get("samples") or 0.0)
                overall = float(stats["All Decks"]["gihwr"])
                lane = (
                    (pair_wr - overall)
                    / self.global_std
                    * games
                    / (games + LANE_PRIOR_GAMES)
                )

        colors = [c for c in card.get("colors", []) if c in self.color_strength]
        color_support = sum(self.color_strength[c] for c in colors)
        off_pips, pip_gap = self._off_pips(card)
        color_gap = sum(
            self.second_strength - self.color_strength[c]
            for c in colors
            if c not in self.main_colors
        )
        return {
            "quality": quality or 0.0,
            "lane": lane,
            "color_support": color_support,
            "color_gap": color_gap,
            "unrated": 1.0 if quality is None else 0.0,
            "off_pips": off_pips,
            "pip_gap": pip_gap,
            **self._share_bins(card),
            **{k: 0.0 for k in WEIGHTS if k.startswith(("lane_", "off_"))},
            **self._group_features(card, quality),
        }

    def _off_pips(self, card: dict) -> tuple[float, float]:
        """Colored mana symbols in the card's (front face's) cost that the
        pool's two main colors can't pay, and those symbols' color gaps summed
        (the smallest, for a hybrid symbol); both 0 before there are two."""
        if len(self.main_colors) < 2:
            return 0.0, 0.0
        cost = str(card.get("mana_cost") or "").split(" // ")[0]
        off, gap = 0, 0.0
        for symbol in re.findall(r"\{(.*?)\}", cost):
            options = symbol.split("/")
            colors = [o for o in options if o in constants.CARD_COLORS]
            if not colors:
                continue
            # Hybrid, {2/W} and Phyrexian symbols can be paid another way.
            if not any(
                o in self.main_colors or o.isdigit() or o == "P" for o in options
            ):
                off += 1
                gap += min(
                    self.second_strength - self.color_strength[c] for c in colors
                )
        return float(off), gap

    def _groups(self):
        """For each K in GROUP_KS, P(group | pool) over 17lands' color groups
        and the most likely group (None before the pool has two colors).

        P(group | pool) is proportional to the group's share of 17lands decks
        times exp(K x the pool's strength in cards the group can cast), where a
        card counts 1 + its quality, as in color_strength."""
        share = getattr(self.metrics, "group_share", {}) or {}
        self.group_names = sorted(share)
        if not self.group_names:
            self.group_p = {}
            return
        prior = np.log(np.array([share[g] for g in self.group_names]))
        fits = np.zeros(len(self.group_names))
        for card in self.pool:
            if "Land" in card.get("types", []):
                continue
            weight = max(0.0, 1.0 + (self._quality(card) or 0.0))
            fits += weight * self._castable_mask(card.get("colors", []))
        two_colors = sum(v > 0 for v in self.color_strength.values()) >= 2
        self.group_p = {}
        for key, k in GROUP_KS.items():
            logp = prior + k * fits
            p = np.exp(logp - logp.max())
            p /= p.sum()
            best = np.zeros(len(p))
            if two_colors:
                best[int(np.argmax(logp))] = 1.0
            self.group_p[key] = (p, best)

    def _castable_mask(self, colors):
        cache = self.metrics.__dict__.setdefault("_castable_cache", {})
        key = (tuple(self.group_names), "".join(sorted(colors)))
        if key not in cache:
            cache[key] = np.array(
                [float(set(colors) <= set(g)) for g in self.group_names]
            )
        return cache[key]

    def _group_vectors(self, card, quality):
        """The card's lane and off-color pips in each group."""
        cache = self.metrics.__dict__.setdefault("_group_cache", {})
        key = (tuple(self.group_names), card.get("name"))
        if key not in cache:
            stats = card.get("deck_colors", {})
            lane = np.zeros(len(self.group_names))
            off = np.zeros(len(self.group_names))
            for i, g in enumerate(self.group_names):
                if quality is not None:
                    pair = stats.get(g, {})
                    pair_wr = float(pair.get("gihwr") or 0.0)
                    if pair_wr > 0:
                        games = float(pair.get("samples") or 0.0)
                        overall = float(stats["All Decks"]["gihwr"])
                        lane[i] = (
                            (pair_wr - overall)
                            / self.global_std
                            * games
                            / (games + LANE_PRIOR_GAMES)
                        )
                off[i] = sum(
                    not any(c in g for c in colors) for colors in self._pips(card)
                )
            cache[key] = (lane, off)
        return cache[key]

    def _group_features(self, card, quality):
        if not self.group_p:
            return {}
        lane, off = self._group_vectors(card, quality)
        out = {}
        for key, (p, best) in self.group_p.items():
            out[f"lane_soft_{key}"] = float(p @ lane)
            out[f"off_soft_{key}"] = float(p @ off)
            out[f"lane_map_{key}"] = float(best @ lane)
            out[f"off_map_{key}"] = float(best @ off)
        return out

    def _reasons(self, features: dict[str, float]) -> list[str]:
        reasons = []
        points = {k: WEIGHTS[k] * v for k, v in features.items()}
        if abs(points["lane"]) >= 1.0:
            better = "Better" if points["lane"] > 0 else "Worse"
            reasons.append(f"{better} in {self.main_archetype} ({points['lane']:+.1f})")
        if points["color_support"] >= 1.0:
            reasons.append(f"Your Colors ({points['color_support']:+.1f})")
        if points["color_gap"] <= -1.0:
            reasons.append(f"Off-Color ({points['color_gap']:+.1f})")
        off = points.get("off_pips", 0.0) + points.get("pip_gap", 0.0)
        if off <= -1.0:
            reasons.append(f"Hard to Cast ({off:+.1f})")
        if features["unrated"]:
            reasons.append("No Win Rate Yet")
        return reasons

    def evaluate_pack(
        self, pack_cards: list[dict], current_pick: int, current_pack: int = 1
    ) -> list[Recommendation]:
        if not pack_cards:
            return []
        safe_pick = max(1, current_pick)

        pack_ranks = {
            str(c.get("name", "Unknown")).strip(): i
            for i, c in enumerate(
                sorted(
                    pack_cards,
                    key=lambda c: float(
                        c.get("deck_colors", {}).get("All Decks", {}).get("gihwr")
                        or 0.0
                    ),
                    reverse=True,
                )
            )
        }

        recommendations = []
        for card in pack_cards:
            try:
                name = str(card.get("name", "Unknown")).strip()
                features = self.pick_features(card)
                if features is None:
                    score, reasons = 0.0, (
                        ["This is the only available option."]
                        if len(pack_cards) == 1
                        else ["Basic Land (Skip)"]
                    )
                    quality, is_elite, on_lane = 0.0, False, True
                else:
                    score = BASE_SCORE + sum(
                        WEIGHTS[k] * v for k, v in features.items()
                    )
                    reasons = self._reasons(features)
                    quality = features["quality"]
                    on_lane = features["color_gap"] == 0
                    is_elite = quality >= self.BOMB_Z_SCORE and on_lane

                recommendations.append(
                    Recommendation(
                        card_name=name,
                        base_win_rate=float(
                            card.get("deck_colors", {})
                            .get("All Decks", {})
                            .get("gihwr")
                            or 0.0
                        ),
                        contextual_score=round(score, 1),
                        z_score=round(quality, 2),
                        wheel_chance=self._wheel_chance(
                            card,
                            safe_pick,
                            pack_ranks.get(name, 99),
                            pack_size=len(pack_cards),
                        ),
                        reasoning=reasons,
                        is_elite=is_elite,
                        archetype_fit=(
                            self.main_archetype if on_lane else "Splash/Speculative"
                        ),
                        tags=card.get("tags", []),
                    )
                )
            except Exception as e:
                logger.warning(f"Advisor error: {e}")
                continue

        return sorted(recommendations, key=lambda x: x.contextual_score, reverse=True)

    def _wheel_chance(
        self, card: dict, pick: int, rank_in_pack: int, pack_size: int = None
    ) -> float:
        # A pack comes back after 8 picks, so it needs 9+ cards now. Pick alone
        # isn't enough: 13- and 14-card packs can't wheel from picks 6 and 7.
        if pick >= 9 or (pack_size is not None and pack_size < 9):
            return 0.0
        try:
            alsa = float(
                card.get("deck_colors", {}).get("All Decks", {}).get("alsa", 0.0)
            )
            if alsa <= pick:
                return 0.0
            coeffs = constants.WHEEL_COEFFICIENTS[min(pick - 1, 5)]
            context_prob = float(np.polyval(coeffs, alsa))
            if rank_in_pack == 0:
                context_prob *= 0.10
            elif rank_in_pack <= 2:
                context_prob *= 0.40
            return max(0.0, min(100.0, context_prob))
        except:
            return 0.0
