"""
src/advisor/engine.py
Scores each card in a pack: a win-rate base blended toward the drafter's
archetype, plus bonuses for bombs and archetype synergy, times castability.
"""

import statistics
import logging
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
    BOMB_Z_SCORE = 1.5
    IWD_PREMIUM_THRESHOLD = 4.5
    # Off-color cards in pack 1 lose PACK1_PRESSURE_STEP of their castability
    # per pick after the first PACK1_PRESSURE_START picks.
    PACK1_PRESSURE_START = 7
    PACK1_PRESSURE_STEP = 0.05
    # Weight on the archetype's win rate in the base score, rising linearly
    # from START at pick 0 to MAX at pick 45.
    ARCH_WEIGHT_START = 0.2
    ARCH_WEIGHT_MAX = 0.9

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

        pack_wrs = []
        for c in pack_cards:
            try:
                wr = float(
                    c.get("deck_colors", {}).get("All Decks", {}).get("gihwr", 0.0)
                )
                if wr > 0:
                    pack_wrs.append(wr)
            except:
                continue

        pack_mean = statistics.mean(pack_wrs) if pack_wrs else self.global_mean
        pack_std = self._pack_spread(pack_wrs)

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
                raw_gihwr = float(stats.get("gihwr", 0.0))
                raw_iwd = float(stats.get("iwd", 0.0))
                card_colors = card.get("colors", [])
                reasons, synergy_bonus = [], 0.0

                # --- STEP 1: Blended Base Score (With Bayesian Smoothing) ---
                base_score = self._calculate_weighted_score(card, safe_pick)

                # --- STEP 2: Bomb Detection ---
                z_score = (raw_gihwr - pack_mean) / pack_std
                power_bonus, iwd_mult = self._bomb_bonus(z_score, raw_iwd)

                # --- STEP 3: Archetype Synergy & 'Glue Cards' ---
                is_on_lane = (
                    all(c in self.main_colors for c in card_colors)
                    if card_colors
                    else True
                )
                if len(self.main_colors) >= 2:
                    synergy_bonus, synergy_reason = self._archetype_synergy(
                        card, raw_gihwr
                    )
                    if synergy_reason:
                        reasons.append(synergy_reason)

                    if is_on_lane:
                        base_score *= self._lane_multiplier(needs_playables)

                # --- STEP 4: Castability (Pip-Sensitive Discipline & Premium Splashing) ---
                cast_mult, cast_reason = self._calculate_castability_v5(
                    card, pack_number, safe_pick, z_score
                )
                if cast_reason:
                    reasons.append(cast_reason)

                # --- STEP 5: Wheel chance (shown, not scored) ---
                wheel_pct = self._wheel_chance(
                    card, safe_pick, pack_ranks.get(name, 99)
                )

                # === MASTER ALGORITHM ===
                final_score = (base_score + power_bonus + synergy_bonus) * cast_mult

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

    def _pack_spread(self, pack_wrs: List[float]) -> float:
        """SD of GIH WR within the pack, which scales the pack z-scores."""
        std = statistics.pstdev(pack_wrs) if len(pack_wrs) > 1 else self.global_std
        return std if std > 0 else self.global_std

    def _bomb_bonus(self, z_score: float, raw_iwd: float) -> Tuple[float, float]:
        """(power bonus, IWD multiplier) for a card well above the pack's average."""
        iwd_mult = (
            1.15 if (raw_iwd > self.IWD_PREMIUM_THRESHOLD and z_score > 1.0) else 1.0
        )
        power_bonus = max(0, z_score * 10 * iwd_mult) if z_score > 0.5 else 0
        return power_bonus, iwd_mult

    def _archetype_synergy(self, card: Dict, raw_gihwr: float) -> Tuple[float, str]:
        """Bonus for a card that does better in the main archetype than overall."""
        arch_wr = float(
            card.get("deck_colors", {}).get(self.main_archetype, {}).get("gihwr", 0.0)
        )
        if arch_wr > 0.0:
            delta = arch_wr - raw_gihwr

            # GLUE CARD DETECTION:
            # If a Common/Uncommon heavily outperforms its global average in our specific lane,
            # it is an archetype "Glue Card" and gets a massive multiplier to push it over generic Rares.
            rarity = str(card.get("rarity", "common")).lower()
            if delta >= 1.0 and rarity in ["common", "uncommon"]:
                bonus = delta * 5.0
                return bonus, f"Archetype Glue (+{bonus:.1f})"
            elif delta >= 1.5:
                bonus = delta * 3.0
                return bonus, f"Archetype Synergy (+{bonus:.1f})"
        return 0.0, ""

    def _lane_multiplier(self, needs_playables: bool) -> float:
        """Base-score multiplier for a card in the main colors."""
        return 1.3 if needs_playables else 1.1

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
            pressure = 1.0 - (
                max(0, ((pack - 1) * 15 + (pick - 1)) - self.PACK1_PRESSURE_START)
                * self.PACK1_PRESSURE_STEP
            )
            return (
                (max(0.2, pressure - 0.2), "Off-Color Gold")
                if len(card_colors) > 1 and off_color_pips > 0
                else (max(0.4, pressure), "Off-Color")
            )

        if not is_on_lane:
            if pack >= 2 and off_color_pips >= 2 and self.fixing_count < 2:
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

    def _wheel_chance(self, card: Dict, pick: int, rank_in_pack: int) -> float:
        """Estimated % chance the card comes back around, for picks 1-8."""
        if pick >= 9:
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

    def _calculate_weighted_score(self, card: Dict, pick_number: int) -> float:
        try:
            stats = card.get("deck_colors", {})
            global_wr = float(stats.get("All Decks", {}).get("gihwr", 0.0))
            arch_weight = min(
                self.ARCH_WEIGHT_MAX,
                self.ARCH_WEIGHT_START
                + (pick_number / self.TOTAL_PICKS)
                * (self.ARCH_WEIGHT_MAX - self.ARCH_WEIGHT_START),
            )
            arch_stats = stats.get(self.main_archetype, {})
            arch_wr = float(arch_stats.get("gihwr", global_wr))

            # BAYESIAN SMOOTHING: Confidently blend global & archetype win rates based on sample size
            samples = int(arch_stats.get("samples", 0))
            confidence = min(1.0, samples / 1000.0)
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
