import io

import drafts

HEADER = (
    "expansion,event_type,draft_id,draft_time,rank,event_match_wins,"
    "event_match_losses,pack_number,pick_number,pick,pick_2,"
    "user_n_games_bucket,user_game_win_rate_bucket,"
    'pack_card_Bear,"pack_card_Ral, Leyline Prodigy",pool_Bear,'
    '"pool_Ral, Leyline Prodigy"\n'
)


def rows(draft_id, skill="0.6", games="50", pick_2=""):
    """Two picks: Ral from Bear and Ral, then Bear."""
    return (
        f'X,PremierDraft,{draft_id},t,gold,3,3,0,0,"Ral, Leyline Prodigy",'
        f"{pick_2},{games},{skill},1,1,0,0\n"
        f"X,PremierDraft,{draft_id},t,gold,3,3,0,1,Bear,,{games},{skill},1,0,0,1\n"
    )


def sample(text, n=10):
    return drafts.sample_drafts(io.StringIO(text), n)


def test_reads_picks_with_quoted_names():
    (draft,) = sample(HEADER + rows("a"))

    assert draft["picks"] == [
        [1, 1, "Ral, Leyline Prodigy", ["Bear", "Ral, Leyline Prodigy"], []],
        [1, 2, "Bear", ["Bear"], ["Ral, Leyline Prodigy"]],
    ]


def test_keeps_only_strong_drafters():
    text = HEADER + rows("a") + rows("b", skill="0.56") + rows("c", games="10")

    assert [d["id"] for d in sample(text)] == ["a"]


def test_leaves_out_drafts_with_a_second_pick():
    text = HEADER + rows("a") + rows("b", pick_2="Bear")

    assert [d["id"] for d in sample(text)] == ["a"]


def test_sample_is_the_lowest_priorities():
    ids = [f"d{i}" for i in range(30)]
    text = HEADER + "".join(rows(i) for i in ids)
    expected = sorted(sorted(ids, key=drafts.draft_priority)[:5])

    assert [d["id"] for d in sample(text, 5)] == expected


def test_keeps_only_drafts_in_the_date_range():
    text = HEADER + rows("a") + rows("b") + rows("c")
    text = text.replace(",a,t,", ",a,2026-01-01 10:00:00,")
    text = text.replace(",b,t,", ",b,2026-01-02 10:00:00,")
    text = text.replace(",c,t,", ",c,2026-01-03 10:00:00,")

    kept = drafts.sample_drafts(
        io.StringIO(text), 10, dates=("2026-01-02", "2026-01-03")
    )

    assert [d["id"] for d in kept] == ["b"]
