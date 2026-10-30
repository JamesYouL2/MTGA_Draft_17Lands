"""
src/advisor/engine.py
The "Compositional Brain" (v5.5 Pro-Tour Architecture)
Updated: Bayesian Smoothing, Top-End/Synergy Tracking, and Premium Removal Splash.
"""

import logging
import math
import numpy as np
import re
from typing import List, Dict, Tuple
from src.advisor.schema import Recommendation
from src import constants
from src.card_utils import get_functional_cmc
from src.advisor.mana_base import count_fixing
from src.utils import normalize_color_string

logger = logging.getLogger(__name__)


class DraftAdvisor:
    TOTAL_PICKS = 45
    CAP_COMBAT_TRICKS = 3
    TARGET_CARD_DRAW = 2
    TARGET_EVASION = 3
    BOMB_Z_SCORE = 1.5
    # Bomb bonus: points per SD of GIH WR above the format mean, from POWER_MIN_Z.
    POWER_PER_Z = 10.0
    POWER_MIN_Z = 0.5
    # Score a card at its overall win rate plus ARCH_WEIGHT times how much
    # better it does in the current archetype, from the first pick. Above 1,
    # this also covers the bonus archetype cards used to get on top. In
    # replays of 30,000 17Lands drafts, 1.5 matched drafters' picks as often
    # as that bonus did, and tracked their wins as well; 0.9 tracked wins
    # worse and 2.0 or more matched fewer picks.
    ARCH_WEIGHT = 1.5
    # Games in hand at which the pair's win rate is trusted fully; with fewer,
    # it is shrunk toward the card's overall win rate.
    ARCH_TRUST_SAMPLES = 1000
    IWD_PREMIUM_THRESHOLD = 4.5

    def __init__(self, set_metrics, taken_cards: List[Dict]):
        self.metrics = set_metrics
        self.pool = taken_cards or []

        # 1. Base statistical baselines
        self.global_mean, self.global_std = self.metrics.get_metrics(
            "All Decks", "gihwr"
        )
        if self.global_mean <= 0:
            self.global_mean = 54.0
        if self.global_std <= 0:
            self.global_std = 4.0

        # 2. Identify established lane
        self.main_colors, self.color_counts = self._identify_main_colors()
        self.main_archetype = (
            normalize_color_string("".join(self.main_colors[:2]))
            if len(self.main_colors) >= 2
            else "All Decks"
        )
        self.active_colors = self.main_colors

        # 3. Analyze Pool Needs
        self.fixing_map = count_fixing(self.pool)
        self.fixing_count = self._count_fixing_cards()

    def evaluate_pack(
        self, pack_cards: List[Dict], current_pick: int, current_pack: int = 1
    ) -> List[Recommendation]:
        if not pack_cards:
            return []
        safe_pick = max(1, min(self.TOTAL_PICKS, current_pick))
        pack_number = max(1, current_pack)

        on_color_pool = [
            c
            for c in self.pool
            if all(col in self.main_colors for col in c.get("colors", []))
        ]
        needs_playables = len(on_color_pool) < 20 and pack_number == 3

        pack_cards_sorted = sorted(
            pack_cards,
            key=lambda c: float(
                c.get("deck_colors", {}).get("All Decks", {}).get("gihwr", 0.0) or 0.0
            ),
            reverse=True,
        )
        pack_ranks = {
            str(c.get("name", "Unknown")).strip(): i
            for i, c in enumerate(pack_cards_sorted)
        }

        recommendations = []
        for card in pack_cards:
            try:
                name = str(card.get("name", "Unknown")).strip()
                stats = card.get("deck_colors", {}).get("All Decks", {})
                raw_gihwr, raw_iwd = (
                    float(stats.get("gihwr", 0.0)),
                    float(stats.get("iwd", 0.0)),
                )
                card_colors = card.get("colors", [])
                reasons = []

                # --- STEP 1: Blended Base Score (With Bayesian Smoothing) ---
                base_score = self._calculate_weighted_score(card)

                # --- STEP 2: Bomb Detection ---
                # Against the format's spread, so a card's bonus doesn't depend
                # on its packmates.
                z_score = (raw_gihwr - self.global_mean) / self.global_std
                iwd_mult = (
                    1.15
                    if (raw_iwd > self.IWD_PREMIUM_THRESHOLD and z_score > 1.0)
                    else 1.0
                )
                power_bonus = (
                    z_score * self.POWER_PER_Z * iwd_mult
                    if z_score > self.POWER_MIN_Z
                    else 0
                )

                # --- STEP 3: Lane ---
                # The card's win rate in the lane's pair is already blended into
                # the base score; this only favors cards in the lane's colors.
                is_on_lane = (
                    all(c in self.main_colors for c in card_colors)
                    if card_colors
                    else True
                )
                if len(self.main_colors) >= 2 and is_on_lane:
                    base_score *= 1.3 if needs_playables else 1.1

                # --- STEP 4: Castability (Pip-Sensitive Discipline & Premium Splashing) ---
                cast_mult, cast_reason = self._calculate_castability_v5(
                    card, pack_number, safe_pick, z_score
                )
                if cast_reason:
                    reasons.append(cast_reason)

                # --- STEP 5: Wheel chance (shown, not scored) ---
                rank_in_pack = pack_ranks.get(name, 99)
                wheel_pct = self._wheel_chance(
                    card, safe_pick, rank_in_pack, pack_size=len(pack_cards)
                )

                # === MASTER ALGORITHM ===
                final_score = (base_score + power_bonus) * cast_mult

                is_basic_land = name in constants.BASIC_LANDS or (
                    "Basic" in card.get("types", []) and "Land" in card.get("types", [])
                )

                if is_basic_land:
                    final_score = 0.0
                    if len(pack_cards) == 1:
                        reasons = ["This is the only available option."]
                    else:
                        reasons = ["Basic Land (Skip)"]

                if iwd_mult > 1.0 and final_score > 0:
                    reasons.insert(0, "TRUE BOMB (High IWD)")

                recommendations.append(
                    Recommendation(
                        card_name=name,
                        base_win_rate=raw_gihwr,
                        contextual_score=round(max(0.0, final_score), 1),
                        z_score=round(z_score, 2),
                        cast_probability=cast_mult,
                        wheel_chance=wheel_pct,
                        functional_cmc=get_functional_cmc(card),
                        reasoning=reasons,
                        is_elite=(
                            (z_score >= self.BOMB_Z_SCORE and cast_mult > 0.4)
                            if not is_basic_land
                            else False
                        ),
                        archetype_fit=(
                            self.main_archetype if is_on_lane else "Splash/Speculative"
                        ),
                        tags=card.get("tags", []),
                    )
                )
            except Exception as e:
                logger.warning(f"Advisor error: {e}")
                continue

        return sorted(recommendations, key=lambda x: x.contextual_score, reverse=True)

    def _identify_main_colors(self) -> Tuple[List[str], Dict[str, float]]:
        color_weights, color_counts = (
            {c: 0.0 for c in constants.CARD_COLORS},
            {c: 0 for c in constants.CARD_COLORS},
        )
        playable_threshold, total_pool_size = (
            self.global_mean - self.global_std,
            len(self.pool),
        )
        for idx, c in enumerate(self.pool):
            try:
                colors = c.get("colors", [])
                wr = float(
                    c.get("deck_colors", {}).get("All Decks", {}).get("gihwr", 0.0)
                )
                if "Land" not in c.get("types", []):
                    for col in colors:
                        color_counts[col] += 1
                if wr < playable_threshold:
                    continue
                base_points = max(
                    0.2, 1.0 + 2.0 * ((wr - self.global_mean) / self.global_std)
                )
                recency_mult = 1.0 + (2.0 * (idx / max(1, total_pool_size)))
                for color in colors:
                    if color in color_weights:
                        color_weights[color] += base_points * recency_mult
            except:
                continue
        sorted_w = sorted(color_weights.items(), key=lambda x: x[1], reverse=True)
        main_colors = []
        if total_pool_size >= 15 and sum(color_counts.values()) > 5:
            threshold = sum(color_counts.values()) * 0.15
            leader_set = [
                v[0]
                for v in sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[
                    :2
                ]
                if v[1] > 0
            ]
            for col, weight in sorted_w:
                if col in leader_set or color_counts[col] >= threshold:
                    main_colors.append(col)
        else:
            for col, weight in sorted_w:
                if weight >= 2.5:
                    main_colors.append(col)
        return main_colors[:3], color_counts

    def _count_fixing_cards(self) -> int:
        """Fixing in the pool: ramp/fixing spells and multicolor lands."""
        count = 0
        for c in self.pool:
            types = c.get("types", [])
            if "fixing_ramp" in c.get("tags", []) or (
                "Land" in types and len(c.get("colors", [])) > 1
            ):
                count += 1
        return count

    def _calculate_castability_v5(
        self, card: Dict, pack: int, pick: int, z_score: float
    ) -> Tuple[float, str]:
        mana_cost = card.get("mana_cost", "")
        card_colors = card.get("colors", [])
        top_2_lane = self.main_colors[:2]

        if mana_cost:
            off_color_pips = 0
            is_on_lane = True
            pips = re.findall(r"\{(.*?)\}", mana_cost)
            for pip in pips:
                options = [c for c in pip.split("/") if c in "WUBRG"]
                if not options:
                    continue
                if any(opt in top_2_lane for opt in options):
                    continue
                else:
                    off_color_pips += 1
                    is_on_lane = False
        else:
            is_on_lane = (
                all(c in top_2_lane for c in card_colors) if card_colors else True
            )
            off_color_pips = 0 if is_on_lane else 1

        if pack == 1:
            if is_on_lane:
                return 1.0, ""
            pressure = 1.0 - (max(0, ((pack - 1) * 15 + (pick - 1)) - 3) * 0.05)
            return (
                (max(0.2, pressure - 0.2), "Off-Color Gold")
                if len(card_colors) > 1 and off_color_pips > 0
                else (max(0.4, pressure), "Off-Color")
            )

        if not is_on_lane:
            if (
                pack >= 2
                and off_color_pips >= 2
                and self.fixing_count < 2
            ):
                return 0.01, "Uncastable (Double Pip)"

            splash_colors = [c for c in card_colors if c not in top_2_lane]
            has_specific_fixing = (
                all(self.fixing_map.get(c, 0) > 0 for c in splash_colors)
                if splash_colors
                else False
            )

            is_premium_removal = "removal" in card.get("tags", []) and z_score >= 1.0

            # Allow premium 1-for-1s to be splashed just like game-winning bombs
            if z_score >= self.BOMB_Z_SCORE or is_premium_removal:
                if off_color_pips == 1:
                    if has_specific_fixing or self.fixing_count >= (
                        4 if pack == 3 else 3
                    ):
                        reason = (
                            "Bomb Splash"
                            if z_score >= self.BOMB_Z_SCORE
                            else "Premium Removal Splash"
                        )
                        return (0.35 if pack == 3 else 0.45), reason
                elif (
                    off_color_pips == 2
                    and get_functional_cmc(card) >= 5
                    and z_score >= self.BOMB_Z_SCORE
                ):
                    if self.fixing_count >= 4:
                        return 0.30, "Greedy Bomb Splash"

            if off_color_pips == 1 and has_specific_fixing:
                return 0.3, "Splashable"

            return 0.01 if pack == 3 else 0.05, "Off-Color"
        return 1.0, ""

    def _wheel_chance(
        self, card: Dict, pick: int, rank_in_pack: int, pack_size: int = None
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

    def _calculate_weighted_score(self, card: Dict) -> float:
        try:
            stats = card.get("deck_colors", {})
            global_wr = float(stats.get("All Decks", {}).get("gihwr", 0.0))
            arch_weight = self.ARCH_WEIGHT
            arch_stats = stats.get(self.main_archetype, {})
            arch_wr = float(arch_stats.get("gihwr", global_wr))

            # BAYESIAN SMOOTHING: Confidently blend global & archetype win rates based on sample size
            samples = int(arch_stats.get("samples", 0))
            confidence = min(1.0, samples / self.ARCH_TRUST_SAMPLES)
            trusted_arch_wr = (arch_wr * confidence) + (global_wr * (1.0 - confidence))

            blended_wr = (
                (global_wr * (1.0 - arch_weight)) + (trusted_arch_wr * arch_weight)
                if (arch_wr > 0 and samples >= 10)
                else global_wr
            )

            return max(
                0.0,
                50.0
                + ((blended_wr - self.global_mean) / max(0.1, self.global_std)) * 15.0,
            )
        except:
            return 0.0
