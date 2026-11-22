import pytest
from unittest.mock import patch
from src.advisor.deck_builder import optimize_deck


@pytest.fixture
def base_deck_and_sb():
    # Create a perfectly legal 40 card deck: 17 Lands, 23 Spells
    base_deck = [
        {"name": f"Forest {i}", "types": ["Land", "Basic"], "count": 1, "colors": ["G"]}
        for i in range(17)
    ]
    base_deck += [
        {
            "name": f"Bear {i}",
            "types": ["Creature"],
            "count": 1,
            "mana_cost": "{1}{G}",
            "cmc": 2,
            "deck_colors": {"All Decks": {"gihwr": 55.0}},
        }
        for i in range(22)
    ]

    # Add one clunky 7-drop spell to the main deck
    base_deck.append(
        {
            "name": "Clunky Behemoth",
            "types": ["Creature"],
            "count": 1,
            "mana_cost": "{6}{G}",
            "cmc": 7,
            "deck_colors": {"All Decks": {"gihwr": 51.0}},
        }
    )

    # Sideboard containing a premium, cheap spell
    base_sb = [
        {
            "name": "Premium 2-Drop",
            "types": ["Creature"],
            "count": 1,
            "mana_cost": "{1}{G}",
            "cmc": 2,
            "deck_colors": {"All Decks": {"gihwr": 60.0}},
        }
    ]

    return base_deck, base_sb


def fake_stats(deck, iterations):
    return {"cast_t2": 50, "iterations": iterations, "size": len(deck)}


@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_swaps_worst_spell_for_best_sideboard_spell(
    mock_sim, base_deck_and_sb
):
    """Power Up: the lowest-rated spell goes to the sideboard and the
    highest-rated castable sideboard spell comes in. No simulation chooses."""
    base_deck, base_sb = base_deck_and_sb

    final_deck, final_sb, final_stats, opt_note = optimize_deck(
        base_deck=base_deck, base_sb=base_sb, archetype_key="G", colors=["G"]
    )

    final_names = [c["name"] for c in final_deck]
    sb_names = [c["name"] for c in final_sb]

    assert sum(c.get("count", 1) for c in final_deck) == 40
    assert "Premium 2-Drop" in final_names
    assert "Clunky Behemoth" not in final_names
    assert sb_names == ["Clunky Behemoth"]
    assert opt_note == "Optimized: Power Up (-Clunky Behemoth, +Premium 2-Drop)"

    # Only the result is simulated, for display.
    mock_sim.assert_called_once()
    assert final_stats["iterations"] == 10000


@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_rates_by_archetype_then_all_decks(mock_sim, base_deck_and_sb):
    """The archetype's GIH WR decides, falling back to All Decks."""
    base_deck, base_sb = base_deck_and_sb
    # In the archetype, Bear 3 is the weakest spell.
    base_deck[17 + 3] = {
        **base_deck[17 + 3],
        "deck_colors": {"All Decks": {"gihwr": 55.0}, "G": {"gihwr": 45.0}},
    }

    final_deck, _, _, opt_note = optimize_deck(base_deck, base_sb, "G", ["G"])

    assert "Bear 3" not in [c["name"] for c in final_deck]
    assert "Clunky Behemoth" in [c["name"] for c in final_deck]
    assert opt_note == "Optimized: Power Up (-Bear 3, +Premium 2-Drop)"


@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_skips_uncastable_and_land_sideboard_cards(
    mock_sim, base_deck_and_sb
):
    """Off-color spells and lands in the sideboard are never swapped in; with
    nothing to bring in, the deck is unchanged but still simulated."""
    base_deck, _ = base_deck_and_sb
    base_sb = [
        {
            "name": "Off-Color Bomb",
            "types": ["Creature"],
            "count": 1,
            "mana_cost": "{1}{R}{R}",
            "cmc": 3,
            "deck_colors": {"All Decks": {"gihwr": 70.0}},
        },
        {
            "name": "Utility Land",
            "types": ["Land"],
            "count": 1,
            "deck_colors": {"All Decks": {"gihwr": 65.0}},
        },
    ]

    final_deck, final_sb, final_stats, opt_note = optimize_deck(
        base_deck, base_sb, "G", ["G"]
    )

    assert final_deck == base_deck
    assert final_sb == base_sb
    assert final_stats is not None
    assert "no castable sideboard spell rates higher" in opt_note


@pytest.mark.parametrize("sb_wr", [51.0, 50.0])
@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_keeps_deck_when_best_sideboard_spell_rates_no_higher(
    mock_sim, base_deck_and_sb, sb_wr
):
    """The swap is made only if the incoming spell rates strictly higher than
    the spell it would cut (51.0 here); a tie or worse leaves the deck as is."""
    base_deck, base_sb = base_deck_and_sb
    base_sb[0]["deck_colors"] = {"All Decks": {"gihwr": sb_wr}}

    final_deck, final_sb, final_stats, opt_note = optimize_deck(
        base_deck, base_sb, "G", ["G"]
    )

    assert final_deck == base_deck
    assert final_sb == base_sb
    assert final_stats is not None
    assert "rates higher" in opt_note


@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_guard_uses_the_pair_rating(mock_sim, base_deck_and_sb):
    """The guard compares the same rating the swap uses: the pair's GIH WR,
    which here puts the sideboard spell below the weakest deck spell even
    though its All Decks rate is higher."""
    base_deck, base_sb = base_deck_and_sb
    base_sb[0]["deck_colors"] = {"All Decks": {"gihwr": 60.0}, "G": {"gihwr": 50.0}}

    final_deck, _, _, opt_note = optimize_deck(base_deck, base_sb, "G", ["G"])

    assert final_deck == base_deck
    assert "rates higher" in opt_note


@patch("src.advisor.deck_builder.simulate_deck", side_effect=fake_stats)
def test_optimize_deck_merges_counts(mock_sim, base_deck_and_sb):
    """A cut copy joins its copies in the sideboard; an added copy joins its
    copies in the deck."""
    base_deck, base_sb = base_deck_and_sb
    base_deck = base_deck[:17] + base_deck[18:]  # drop Bear 0: 39 cards
    base_deck.append({**base_sb[0], "count": 1})  # one Premium already in: 40
    base_sb = [
        {**base_sb[0], "count": 1},
        {
            "name": "Clunky Behemoth",
            "types": ["Creature"],
            "count": 2,
            "mana_cost": "{6}{G}",
            "cmc": 7,
            "deck_colors": {"All Decks": {"gihwr": 51.0}},
        },
    ]

    final_deck, final_sb, _, _ = optimize_deck(base_deck, base_sb, "G", ["G"])

    deck_counts = {c["name"]: c.get("count", 1) for c in final_deck}
    sb_counts = {c["name"]: c.get("count", 1) for c in final_sb}
    assert deck_counts["Premium 2-Drop"] == 2
    assert "Clunky Behemoth" not in deck_counts
    assert sb_counts == {"Clunky Behemoth": 3}
    # The inputs are not mutated.
    assert base_sb[1]["count"] == 2


def test_optimize_deck_rejects_invalid_deck_sizes():
    """Verify the optimizer instantly bails if given an illegal deck size."""
    # Pass a deck with only 10 cards
    deck = [{"name": "Card", "count": 10}]
    final_deck, final_sb, final_stats, opt_note = optimize_deck(
        deck, [], "All Decks", ["W"]
    )

    assert final_stats is None
    assert final_deck == deck
