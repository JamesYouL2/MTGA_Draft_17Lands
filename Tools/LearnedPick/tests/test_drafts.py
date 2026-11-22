import csv
import io

from drafts import sample_two

HEADER = [
    "draft_id",
    "event_match_wins",
    "event_match_losses",
    "pack_number",
    "pick_number",
    "pick",
    "user_n_games_bucket",
    "user_game_win_rate_bucket",
    "pack_card_Alpha",
    "pack_card_Beta",
    "pool_Alpha",
    "pool_Beta",
]


def dump(drafts):
    """CSV lines for {draft_id: (skill, games)}, two picks each."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(HEADER)
    for draft_id, (skill, games) in drafts.items():
        writer.writerow([draft_id, 3, 3, 0, 0, "Alpha", games, skill, 1, 1, 0, 0])
        writer.writerow([draft_id, 3, 3, 0, 1, "Beta", games, skill, 0, 1, 1, 0])
    return out.getvalue().splitlines(keepends=True)


def test_strong_sample_holds_only_strong_drafters_and_all_holds_anyone():
    drafts = {f"d{i:02d}": ((0.62, 100) if i % 3 == 0 else (0.5, 100)) for i in range(60)}
    drafts["weak_games"] = (0.7, 10)
    out = sample_two(dump(drafts), 5, 10)
    strong = [d for d in out if "strong" in d["samples"]]
    everyone = [d for d in out if "all" in d["samples"]]
    assert len(strong) == 5 and len(everyone) == 10
    assert all(d["strong"] and d["skill"] >= 0.6 and d["games"] >= 50 for d in strong)
    assert all(len(d["picks"]) == 2 for d in out)
    assert out[0]["picks"][1] == [1, 2, "Beta", ["Beta"], ["Alpha"]]


def test_sample_is_repeatable_and_salt_changes_it():
    drafts = {f"d{i:02d}": (0.62, 100) for i in range(40)}
    ids = lambda salt: [d["id"] for d in sample_two(dump(drafts), 5, 5, salt)]
    assert ids("a") == ids("a")
    assert ids("a") != ids("b")


def test_weak_sample_holds_only_weak_drafters_and_leaves_the_others_unchanged():
    drafts = {f"d{i:02d}": [(0.62, 100), (0.5, 100), (0.54, 100)][i % 3] for i in range(90)}
    drafts["weak_few_games"] = (0.4, 10)
    without = sample_two(dump(drafts), 5, 10)
    out = sample_two(dump(drafts), 5, 10, n_weak=6)
    weak = [d for d in out if "weak" in d["samples"]]
    assert len(weak) == 6
    assert all(d["weak"] and d["skill"] < 0.52 and d["games"] >= 50 for d in weak)
    assert not any(d["weak"] for d in out if d["skill"] >= 0.52 or d["games"] < 50)
    for name in ("strong", "all"):
        assert [d["id"] for d in out if name in d["samples"]] == [
            d["id"] for d in without if name in d["samples"]
        ]
