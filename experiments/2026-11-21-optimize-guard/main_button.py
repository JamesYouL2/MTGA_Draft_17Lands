"""Today's main Auto-Optimize (before simplify/optimize-power-up), copied verbatim
from origin/main edfab59 for the base head of experiments/2026-11-21-optimize-guard.
Only the imports are new."""

from src import constants
from src.card_utils import get_functional_cmc
from src.mana_cost import mana_color_demand
from src.advisor.mana_base import is_castable, create_basic_lands
from src.advisor.simulator import simulate_deck


def optimize_deck(base_deck, base_sb, archetype_key, colors):
    total_cards = sum(c.get("count", 1) for c in base_deck)
    if total_cards != 40:
        return (
            base_deck,
            base_sb,
            None,
            f"Error: Deck must be exactly 40 cards to optimize (currently {total_cards}).",
        )

    spells = [c for c in base_deck if "Land" not in c.get("types", [])]
    lands = [c for c in base_deck if "Land" in c.get("types", [])]
    sb_spells = [
        c
        for c in base_sb
        if "Land" not in c.get("types", []) and is_castable(c, colors, strict=True)
    ]

    def get_wr(c):
        return float(
            c.get("deck_colors", {}).get(archetype_key, {}).get("gihwr")
            or c.get("deck_colors", {}).get("All Decks", {}).get("gihwr", 0.0)
        )

    spells.sort(key=get_wr)
    sb_spells.sort(key=get_wr, reverse=True)

    worst_spell = spells[0] if spells else None
    best_sb_spell = sb_spells[0] if sb_spells else None

    highest_cmc_spell = (
        max(spells, key=lambda c: get_functional_cmc(c)) if spells else None
    )
    cheap_sb_spells = [c for c in sb_spells if get_functional_cmc(c) <= 2]
    best_cheap_sb = cheap_sb_spells[0] if cheap_sb_spells else None

    basic_lands = [
        c
        for c in lands
        if "Basic" in c.get("types", []) or c.get("name") in constants.BASIC_LANDS
    ]
    cuttable_land = basic_lands[0] if basic_lands else None
    colorless_utility_lands = [
        c
        for c in lands
        if not c.get("colors")
        and not any(fn in c.get("name", "").lower() for fn in constants.FIXING_NAMES)
    ]
    worst_colorless_land = (
        min(colorless_utility_lands, key=get_wr) if colorless_utility_lands else None
    )

    permutations = [("Base Deck", base_deck, base_sb)]

    def swap_cards(deck, sb, out_card, in_card):
        new_deck = []
        new_sb = list(sb)
        removed = False

        for c in deck:
            if not removed and c["name"] == out_card["name"]:
                if c.get("count", 1) > 1:
                    new_c = dict(c)
                    new_c["count"] -= 1
                    new_deck.append(new_c)
                removed = True
            else:
                new_deck.append(c)

        if removed and in_card:
            added = False
            for c in new_deck:
                if c["name"] == in_card["name"]:
                    new_c = dict(c)
                    new_c["count"] += 1
                    new_deck = [
                        new_c if x["name"] == in_card["name"] else x for x in new_deck
                    ]
                    added = True
                    break
            if not added:
                in_c = dict(in_card)
                in_c["count"] = 1
                new_deck.append(in_c)

            sb_removed = False
            final_sb = []
            for c in new_sb:
                if not sb_removed and c["name"] == in_card["name"]:
                    if c.get("count", 1) > 1:
                        new_c = dict(c)
                        new_c["count"] -= 1
                        final_sb.append(new_c)
                    sb_removed = True
                else:
                    final_sb.append(c)
            new_sb = final_sb

            sb_added = False
            for c in new_sb:
                if c["name"] == out_card["name"]:
                    new_c = dict(c)
                    new_c["count"] += 1
                    new_sb = [
                        new_c if x["name"] == out_card["name"] else x for x in new_sb
                    ]
                    sb_added = True
                    break
            if not sb_added:
                out_c = dict(out_card)
                out_c["count"] = 1
                new_sb.append(out_c)

        return new_deck, new_sb

    if (
        highest_cmc_spell
        and best_cheap_sb
        and highest_cmc_spell["name"] != best_cheap_sb["name"]
    ):
        d, s = swap_cards(base_deck, base_sb, highest_cmc_spell, best_cheap_sb)
        permutations.append(
            (
                f"Curve Lower (-{highest_cmc_spell['name']}, +{best_cheap_sb['name']})",
                d,
                s,
            )
        )

    if worst_spell and best_sb_spell and worst_spell["name"] != best_sb_spell["name"]:
        d, s = swap_cards(base_deck, base_sb, worst_spell, best_sb_spell)
        permutations.append(
            (f"Power Up (-{worst_spell['name']}, +{best_sb_spell['name']})", d, s)
        )

    if worst_spell and cuttable_land:
        d, s = swap_cards(base_deck, base_sb, worst_spell, cuttable_land)
        permutations.append((f"Play 18 Lands (-{worst_spell['name']})", d, s))

    if cuttable_land and best_sb_spell:
        d, s = swap_cards(base_deck, base_sb, cuttable_land, best_sb_spell)
        permutations.append((f"Play 16 Lands (+{best_sb_spell['name']})", d, s))

    if worst_colorless_land:
        pip_counts = mana_color_demand(spells, colors)

        best_basic_color = (
            max(pip_counts, key=pip_counts.get)
            if any(pip_counts.values())
            else (
                archetype_key[0]
                if archetype_key and archetype_key != "All Decks"
                else "W"
            )
        )
        synth_basic = create_basic_lands(best_basic_color, 1)[0]
        d, s = swap_cards(base_deck, base_sb, worst_colorless_land, synth_basic)
        permutations.append(
            (f"Fix Mana Base (-{worst_colorless_land['name']}, +Basic Land)", d, s)
        )

    basic_types = list(set(c["name"] for c in basic_lands))
    if len(basic_types) >= 2:
        for type_add in basic_types:
            for type_sub in basic_types:
                if type_add == type_sub:
                    continue
                card_sub = next((c for c in basic_lands if c["name"] == type_sub), None)
                card_add = next((c for c in basic_lands if c["name"] == type_add), None)
                if not card_add:
                    color_map_inv = {
                        "Plains": "W",
                        "Island": "U",
                        "Swamp": "B",
                        "Mountain": "R",
                        "Forest": "G",
                        "Wastes": "C",
                    }
                    synth_color = color_map_inv.get(type_add, "W")
                    card_add = create_basic_lands(synth_color, 1)[0]

                if card_sub:
                    d, s = swap_cards(base_deck, base_sb, card_sub, card_add)
                    permutations.append(
                        (f"Optimize Mana (+{type_add}, -{type_sub})", d, s)
                    )

    best_score = -9999
    best_perm = permutations[0]

    for desc, p_deck, p_sb in permutations:
        stats = simulate_deck(p_deck, iterations=500)
        if not stats:
            continue
        score = (
            stats["cast_t2"]
            + stats["cast_t3"]
            + stats["cast_t4"]
            + (stats["curve_out"] * 2)
            - stats["mulligans"]
            - (stats["screw_t3"] * 1.5)
            - (stats["color_screw_t3"] * 2.0)
            - (stats["flood_t5"] * 1.5)
        )
        if score > best_score:
            best_score = score
            best_perm = (desc, p_deck, p_sb)

    final_deck, final_sb = best_perm[1], best_perm[2]
    final_stats = simulate_deck(final_deck, iterations=10000)
    return final_deck, final_sb, final_stats, f"Optimized: {best_perm[0]}"
