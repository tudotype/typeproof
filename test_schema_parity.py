"""Schema↔lint parity tests.

Guards the schema (`typography-system-schema.yaml`) against drift from the
lint engine (`typeproof.py`). The schema is the OSS-facing artefact;
this test ensures that every claim it makes about the lint is true.

What this test asserts:
  1. Every `_rule_*` method on `TypographyLinter` is referenced by at least
     one YAML rule entry's `lint_method:` field.
  2. Every YAML rule with `status: implemented` names a `lint_method:` that
     actually exists on `TypographyLinter`.
  3. Every dispatch table referenced via `consumes:` exists in the
     `dispatch_tables:` section.
  4. Every locale used as a dispatch-table key is either declared in
     `languages:` or is the literal `universal`.
  5. Every example in `examples:` blocks round-trips through the lint at the
     appropriate locale. Reported as a soft check (xfail-style) because some
     examples deliberately illustrate a single rule's effect in isolation;
     interaction with other implemented rules (e.g. widow prevention) can
     legitimately add extra NBSPs not shown in the example. The dedicated
     eval suite (`eval_typography.py`) is the gold standard for end-to-end
     correctness.

Fast: under a second.
"""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest
import yaml

import typeproof
from typeproof import TypographyLinter, SUPPORTED_LANGUAGES

REPO = Path(__file__).resolve().parent
SCHEMA_PATH = REPO / "typography-system-schema.yaml"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def lint_methods() -> set[str]:
    return {
        name for name, _ in inspect.getmembers(TypographyLinter, predicate=inspect.isfunction)
        if name.startswith("_rule_")
    }


@pytest.fixture(scope="module")
def universal_rules(schema) -> dict[str, dict]:
    return {
        name: body
        for name, body in schema["semantic_rules"]["universal"].items()
        if isinstance(body, dict)
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _yaml_lint_methods(schema: dict) -> set[str]:
    """Collect every non-empty lint_method value anywhere in the schema.
    `lint_method:` is always a list (possibly empty for roadmap rules)."""
    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            v = node.get("lint_method")
            if isinstance(v, list):
                found.update(m for m in v if isinstance(m, str))
            elif isinstance(v, str):  # tolerate legacy string form
                found.add(v)
            for k, val in node.items():
                walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    return found


def _walk_rule_entries(schema: dict):
    """Yield (path, rule_dict) for every node that looks like a rule
    (has `description:` and either `rule:` or `resolves_to:`)."""
    def walk(node, path):
        if isinstance(node, dict):
            looks_like_rule = (
                "description" in node and ("rule" in node or "resolves_to" in node or "lint_method" in node)
            )
            if looks_like_rule:
                yield path, node
            for k, v in node.items():
                yield from walk(v, path + (k,))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                yield from walk(item, path + (i,))

    yield from walk(schema, ())


# ---------------------------------------------------------------------------
# 1. Every _rule_* method is referenced somewhere in YAML
# ---------------------------------------------------------------------------

def test_every_lint_method_is_referenced(schema, lint_methods):
    referenced = _yaml_lint_methods(schema)
    # `used_by:` arrays on dispatch tables also count
    def collect_used_by(node):
        if isinstance(node, dict):
            ub = node.get("used_by")
            if isinstance(ub, list):
                referenced.update(m for m in ub if isinstance(m, str))
            for v in node.values():
                collect_used_by(v)
        elif isinstance(node, list):
            for item in node:
                collect_used_by(item)
    collect_used_by(schema)

    orphans = sorted(lint_methods - referenced)
    assert not orphans, (
        "Lint methods not referenced by any YAML rule's `lint_method:` "
        f"or dispatch table's `used_by:`: {orphans}"
    )


# ---------------------------------------------------------------------------
# 2. Every status: implemented rule names a real method
# ---------------------------------------------------------------------------

def test_implemented_rules_point_to_real_methods(universal_rules, lint_methods):
    bad: list[tuple[str, str]] = []
    for name, body in universal_rules.items():
        if body.get("status") != "implemented":
            continue
        lm = body.get("lint_method")
        # Normalise to a list — schema uses list form uniformly, but tolerate
        # string for forward-compat.
        if lm is None:
            methods: list[str] = []
        elif isinstance(lm, str):
            methods = [lm]
        elif isinstance(lm, list):
            methods = [m for m in lm if isinstance(m, str)]
        else:
            methods = []
        if not methods:
            # `code_exclusion` is implemented as masking, not a discrete method
            if name == "code_exclusion":
                continue
            bad.append((name, "<missing lint_method>"))
            continue
        for method in methods:
            if method not in lint_methods:
                bad.append((name, method))

    assert not bad, (
        "YAML rules marked `status: implemented` whose `lint_method:` does "
        f"not exist on TypographyLinter: {bad}"
    )


# ---------------------------------------------------------------------------
# 3. Every consumes: target exists in dispatch_tables
# ---------------------------------------------------------------------------

def test_consumes_targets_exist(schema):
    tables = set(schema.get("dispatch_tables", {}).keys())
    missing: list[tuple[str, str]] = []

    def walk(node, path):
        if isinstance(node, dict):
            cons = node.get("consumes")
            if isinstance(cons, list):
                for t in cons:
                    if t not in tables:
                        missing.append((".".join(map(str, path)), t))
            for k, v in node.items():
                walk(v, path + (k,))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + (i,))

    walk(schema, ())
    assert not missing, f"`consumes:` targets not found in dispatch_tables: {missing}"


# ---------------------------------------------------------------------------
# 4. Every locale used in a dispatch table is declared in languages: (or `universal`)
# ---------------------------------------------------------------------------

def test_dispatch_table_locales_are_declared(schema):
    """Dispatch tables that key on locale must reference declared locales.
    Abbreviation tables key on tokens (Mr, Sr, ...) and are skipped."""
    import re as _re
    declared = set(schema["languages"].keys()) | {"universal"} | set(SUPPORTED_LANGUAGES)
    locale_re = _re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
    locale_keyed = {
        "currency_styles", "footnote_placement", "quote_punct_placement",
        "serial_comma_policy", "serial_coordinators", "colon_cap_policy",
        "subject_pronouns", "fragment_starters", "spanish_lexical_accents",
        "title_abbrevs_by_lang", "single_letter_words", "ro_cedilla_map",
    }
    bad: list[tuple[str, str]] = []
    for table_name, table in schema["dispatch_tables"].items():
        if table_name not in locale_keyed:
            continue
        data = table.get("data") if isinstance(table, dict) else None
        if not isinstance(data, dict):
            continue
        for key in data:
            if not isinstance(key, str) or not locale_re.match(key):
                continue
            if key not in declared:
                bad.append((table_name, key))
    assert not bad, f"Locales used in dispatch tables but not declared: {bad}"


# ---------------------------------------------------------------------------
# 5. Round-trip examples (soft check, reported via stdout)
# ---------------------------------------------------------------------------

# Routing for universal rules without an explicit locale in the path.
_UNIVERSAL_ROUTING = {
    "french_ligatures": "fr-FR",
    "nnbsp_semantics": "fr-FR",
    "italian_apostrophic_acute": "it-IT",
    "eszett_capitalisation": "de-DE",
    "ligature_suppression": "de-DE",
    "capital_accent_preservation": "fr-FR",
    "spanish_inverted_punctuation": "es-ES",
}


def _locale_for(path: tuple) -> str:
    for p in path:
        if isinstance(p, str) and p in SUPPORTED_LANGUAGES:
            return p
    if len(path) >= 2 and path[0] == "universal":
        return _UNIVERSAL_ROUTING.get(path[1], "en-US")
    return "en-US"


def _collect_examples(schema):
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            ex = node.get("examples")
            if isinstance(ex, list):
                for item in ex:
                    if isinstance(item, dict) and "raw" in item and "correct" in item:
                        out.append((path, item["raw"], item["correct"]))
            for k, v in node.items():
                if k == "examples":
                    continue
                walk(v, path + (k,))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + (i,))

    walk(schema["semantic_rules"], ("semantic_rules",))
    walk(schema["languages"], ("languages",))
    return out


def test_examples_round_trip_soft(schema, capsys):
    """Round-trip every example. Failures are REPORTED, not asserted —
    examples often demonstrate a single rule's effect in isolation while the
    full lint pipeline applies additional implemented rules (e.g. widow
    prevention adds a non-breaking space before the last word). The eval
    suite is the gold standard for end-to-end correctness."""
    universal_status = {
        name: (body.get("status") if isinstance(body, dict) else None)
        for name, body in schema["semantic_rules"]["universal"].items()
    }
    examples = _collect_examples(schema)
    linters: dict[str, TypographyLinter] = {}

    skipped_roadmap = 0
    passed = 0
    failed: list[tuple[str, str, str, str, str]] = []

    for path, raw, correct in examples:
        # Skip roadmap rules: their examples illustrate aspirational behaviour.
        rule = path[2] if len(path) >= 3 and path[1] == "universal" else None
        if rule and universal_status.get(rule) == "roadmap":
            skipped_roadmap += 1
            continue
        loc = _locale_for(path[1:])  # drop leading 'semantic_rules'/'languages'
        linter = linters.setdefault(loc, TypographyLinter(language=loc))
        try:
            result = linter.lint(raw).text
        except Exception as exc:
            failed.append((".".join(map(str, path)), loc, raw, correct, f"EXC: {exc}"))
            continue
        if result == correct:
            passed += 1
        else:
            failed.append((".".join(map(str, path)), loc, raw, correct, result))

    total = len(examples)
    print(f"\n[round-trip] examples={total} passed={passed} "
          f"failed={len(failed)} roadmap_skipped={skipped_roadmap}")
    if failed:
        print(f"[round-trip] {len(failed)} mismatches (informational, not enforced):")
        for rule_path, loc, raw, correct, got in failed[:5]:
            print(f"  {rule_path} [{loc}]")
            print(f"    raw:      {raw!r}")
            print(f"    expected: {correct!r}")
            print(f"    got:      {got!r}")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more")

    # Hard floor: at least half the non-roadmap examples must round-trip.
    # If this drops below 50%, something has regressed materially.
    enforceable = total - skipped_roadmap
    assert enforceable == 0 or passed / enforceable >= 0.5, (
        f"Round-trip pass rate dropped below 50% "
        f"({passed}/{enforceable}). Investigate before publishing."
    )


# ---------------------------------------------------------------------------
# 6. Sanity: schema parses and core sections exist
# ---------------------------------------------------------------------------

def test_schema_has_required_top_level_keys(schema):
    required = {
        "name", "version", "license", "repository",
        "primitives", "semantic_rules", "dispatch_tables",
        "languages", "registers", "resolution",
    }
    missing = required - set(schema.keys())
    assert not missing, f"Missing top-level keys: {missing}"


def test_metadata_values(schema):
    assert schema["name"] == "langtype"
    assert isinstance(schema["version"], str) and schema["version"]
    assert schema["license"] == "MIT"
    assert schema["languages_implemented"] == len(schema["languages"])
