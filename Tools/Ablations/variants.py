"""Standalone one-factor source edits and an equivalent fast replay path."""
import ast
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ENGINE = "src/advisor/engine.py"
DECK_BUILDER = "src/advisor/deck_builder.py"
DECK_SCORER = "src/advisor/deck_scorer.py"
BASE_SHA = "99dc21e1c894d03ce155cdc494063c3d5c93b358"

COMPOSITION = {
    "no-curve-heavy": "Curve Too Heavy",
    "no-creature-quota": "Critical: Needs Creatures",
    "no-artifact-synergy": "Artifact Synergy",
    "no-graveyard-synergy": "Graveyard Synergy",
    "no-counters-synergy": "Counters Synergy",
    "no-fixing-hunger": "Critical: Needs Fixing",
    "no-bomb-fixing": "Enables Bomb Splash",
    "no-premium-fixing": "Premium Fixing",
    "no-removal-need": "Critical: Needs Removal",
    "no-removal-saturation": "Removal Saturated",
    "no-early-plays": "Critical: Needs 2-Drops",
}
PICK_VARIANTS = ["no-composition", *COMPOSITION, "no-power-bonus", "no-iwd",
                 "no-lane-boost", "no-archetype", "no-shrinkage", "no-castability"]
MC = {"no-mc-color": ("color_screw_t3", 10.0, 2.5),
      "no-mc-screw": ("screw_t3", 22.0, 1.5),
      "no-mc-flood": ("flood_t5", 27.0, 1.5)}
FEATURES = {"no-two-color-bonus": "two_colors", "no-domain-bonus": "domain_supported",
            "no-fixing-penalty": "missing_fixing"}
DECK_VARIANTS = [*MC, "no-mc-all", *FEATURES]
ALL_VARIANTS = PICK_VARIANTS + DECK_VARIANTS


def assert_baseline():
    """Refuse to stack a run on an experiment branch or dirty app source."""
    check = subprocess.run(["git", "diff", "--quiet", BASE_SHA, "--", "src"], cwd=ROOT)
    if check.returncode:
        raise SystemExit(f"Application source differs from frozen baseline {BASE_SHA}; use the suite/index branch")


def replace_span(source, node, replacement):
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[:node.lineno - 1])) + node.col_offset
    end = sum(map(len, lines[:node.end_lineno - 1])) + node.end_col_offset
    return source[:start] + replacement + source[end:]


def function(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def has_text(node, text):
    return any(isinstance(n, ast.Constant) and n.value == text for n in ast.walk(node))


def assignment(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


def variant_source(variant, source=None):
    """Return (path, source), changing exactly one factor against BASE_SHA."""
    path = ENGINE if variant in PICK_VARIANTS else (DECK_SCORER if variant in FEATURES else DECK_BUILDER)
    source = source if source is not None else (ROOT / path).read_text()
    tree = ast.parse(source)
    if variant in ("no-composition", "no-castability"):
        name = "_calculate_composition_bonus" if variant == "no-composition" else "_calculate_castability_v5"
        fn = function(tree, name)
        first, last = fn.body[0], fn.body[-1]
        first.end_lineno, first.end_col_offset = last.end_lineno, last.end_col_offset
        return path, replace_span(source, first, 'return 1.0, ""')
    if variant in COMPOSITION:
        fn = function(tree, "_calculate_composition_bonus")
        if variant == "no-premium-fixing":
            node = next(n for n in ast.walk(fn) if isinstance(n, ast.IfExp) and has_text(n, COMPOSITION[variant]))
            return path, replace_span(source, node, '(1.0, "")')
        nodes = [n for n in ast.walk(fn) if isinstance(n, ast.If) and has_text(n, COMPOSITION[variant])]
        node = min(nodes, key=lambda n: n.end_lineno - n.lineno)
        return path, replace_span(source, node.test, "False")
    names = {"no-power-bonus": ("power_bonus", "0.0"), "no-iwd": ("iwd_mult", "1.0"),
             "no-archetype": ("arch_weight", "0.0"), "no-shrinkage": ("confidence", "1.0")}
    if variant in names:
        name, value = names[variant]
        return path, replace_span(source, assignment(tree, name).value, value)
    if variant == "no-lane-boost":
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.AugAssign)
                    and isinstance(n.target, ast.Name) and n.target.id == "base_score")
        return path, replace_span(source, node.value, "1.0")
    if variant in FEATURES:
        weights = assignment(tree, "WEIGHTS").value
        node = next(v for k, v in zip(weights.keys, weights.values) if k.value == FEATURES[variant])
        return path, replace_span(source, node, "0.0")
    if variant == "no-mc-all":
        fn = function(tree, "suggest_deck")
        node = next(n for n in ast.walk(fn) if isinstance(n, ast.If)
                    and isinstance(n.test, ast.Name) and n.test.id == "opt_stats")
        return path, replace_span(source, node.test, "False")
    if variant in MC:
        stat = MC[variant][0]
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                    and has_text(n.test, stat))
        return path, replace_span(source, node.test, "False")
    raise ValueError(variant)


def advisor_class(source):
    import src.advisor.engine as engine
    scope = dict(vars(engine))
    exec(compile(source, ENGINE, "exec"), scope)
    return scope["DraftAdvisor"]


def traced_class(source):
    tree = ast.parse(source)
    fn = function(tree, "evaluate_pack")
    for node in ast.walk(fn):
        for field in ("body", "orelse"):
            statements = getattr(node, field, None)
            if not isinstance(statements, list):
                continue
            for i, stmt in list(enumerate(statements)):
                if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "base_score" for t in stmt.targets):
                    statements.insert(i + 1, ast.parse("raw_base_score = base_score").body[0])
                if isinstance(stmt, ast.If) and has_text(stmt, "TRUE BOMB (High IWD)"):
                    trace = "self._trace.append((card, raw_base_score, base_score, power_bonus, cast_mult, role_mult, iwd_mult, final_score, raw_gihwr, (1.3 if needs_playables else 1.1) if len(self.main_colors) >= 2 and is_on_lane else 1.0))"
                    statements.insert(i, ast.parse(trace).body[0])
    ast.fix_missing_locations(tree)
    import src.advisor.engine as engine
    scope = dict(vars(engine))
    exec(compile(tree, ENGINE, "exec"), scope)
    return scope["DraftAdvisor"]


def scores_from_trace(advisor, variant, cls, pack_no):
    from src import constants
    other = object.__new__(cls)
    other.__dict__.update(advisor.__dict__)
    out = {}
    for card, raw_base, base, power, cast, role, iwd, final, wr, lane_mult in advisor._trace:
        if variant == "no-composition":
            role = 1.0
        elif variant in COMPOSITION:
            role = other._calculate_composition_bonus(card, pack_no)[0]
        elif variant == "no-power-bonus":
            power = 0.0
        elif variant == "no-iwd":
            power /= iwd
        elif variant == "no-lane-boost":
            base = raw_base
        elif variant in ("no-archetype", "no-shrinkage"):
            if variant == "no-archetype":
                base = other._score_from_wr(wr) * lane_mult
            else:
                base = other._calculate_weighted_score(card, advisor._pick) * lane_mult
        elif variant == "no-castability":
            cast = 1.0
        score = (base + power) * cast * role
        name = str(card.get("name", "Unknown")).strip()
        if name in constants.BASIC_LANDS or ("Basic" in card.get("types", []) and "Land" in card.get("types", [])):
            score = 0.0
        out.setdefault(name, round(max(0.0, score), 1))
    return out
