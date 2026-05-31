---
name: typeproof
description: Typography linting and correction using the Typeproof pipeline
---

# Typeproof

Typeproof is a language-aware typographic correction system. It uses a deterministic linter (`typeproof.py`) for 50+ Unicode-level rules across 20+ languages, backed by a YAML schema as the single source of truth.

## When to use this skill

- Linting or correcting text for typographic errors (quotes, dashes, spacing, diacritics, etc.)
- Editing the typography schema (`typography-system-schema.yaml`)
- Working on the WordPress plugin (`wp-plugin/`)
- Regenerating training data or running the fine-tuning pipeline
- Adding new languages or rules to the system

## Repository layout

```
typeproof.py                 ← Standalone linter (3,400+ lines, zero deps)
typography-system-schema.yaml      ← Source of truth for all rules
generate_dataset.py                ← Schema → JSONL training pairs
train_typography.py                ← Unsloth LoRA fine-tuning
eval_typography.py                 ← Ground-truth evaluation
test_typeproof.py            ← Linter test suite
wp-plugin/                         ← WordPress plugin (PHP wrapper)
docs/thinking.md                   ← Design decision log
```

## Linter CLI usage

```bash
# Basic correction (defaults to en-US)
python3 typeproof.py "He said \"hello\"..."

# Specify language
python3 typeproof.py --lang fr-FR "Il a dit \"bonjour\"..."

# JSON output with correction metadata
python3 typeproof.py --json --lang pt-PT "Ele disse \"olá\"..."

# Colored diff output
python3 typeproof.py --diff --lang de-DE 'Er sagte "Hallo"...'

# Register-sensitive correction
python3 typeproof.py --register editorial --lang en-US "The company's Q1 results..."

# From file
python3 typeproof.py --file article.txt --lang en-GB --json

# From stdin
echo 'Some text with "quotes"' | python3 typeproof.py --lang en-US
```

### CLI flags

| Flag | Description |
|------|-------------|
| `--lang` | BCP 47 language code (default: `en-US`) |
| `--register` | Context: `editorial`, `marketing`, `ui`, `literary` |
| `--json` | Structured JSON output with corrections array |
| `--diff` | ANSI-colored before/after diff |
| `--file` | Read input from file path |
| `--verbose` | Print per-rule stats to stderr |

### JSON output structure

```json
{
  "text": "corrected text",
  "original": "original text",
  "language": "en-US",
  "register": null,
  "corrections": [
    {
      "position": 8,
      "original": "\"hello\"",
      "replacement": "\u201chello\u201d",
      "rule": "quotation_marks",
      "description": "Replaced straight quotes with curly quotes (en-US)"
    }
  ],
  "stats": {
    "total_corrections": 1,
    "by_rule": { "quotation_marks": 1 }
  }
}
```

## Testing

```bash
# Run full test suite
pytest test_typeproof.py -v

# Run specific test
pytest test_typeproof.py -v -k "test_french"

# Quick smoke test
python3 typeproof.py --json --lang en-US '"Hello" world -- test...'
```

## Pipeline commands

```bash
# 1. Regenerate training data from schema
python3 generate_dataset.py

# 2. Fine-tune model (requires Unsloth + GPU)
python3 train_typography.py

# 3. Evaluate against ground truth
python3 eval_typography.py
```

## Schema editing rules

When editing `typography-system-schema.yaml`:

1. Every rule MUST have `description` and either `resolves_to` or `rule`
2. Every language-specific rule needs `examples` with `raw` and `correct` fields
3. New languages inherit from closest parent; override only differences
4. Spacing uses named patterns from `primitives.spacing_patterns` — never inline raw Unicode
5. Ambiguous conventions get a `notes` field
6. Register-sensitive rules are marked `register_sensitive: true`

## Architecture: 8-phase pipeline

See `references/rule-phases.md` for the full pipeline documentation.

**Summary:**
1. Exclusion masking (code, URLs, emails protected)
2. NFC normalization + zero-width cleanup
3. Language-specific preprocessing (diacritics, ligatures, accents)
4. Universal substitution rules (quotes, dashes, ellipsis, symbols)
4b. Universal structural rules (nested parens, NBSP between initials)
5. Language-specific post-processing (abbreviations, NBSP, ordinals)
6. Abbreviation haplology (prevents double periods)
7. Unmask exclusions
8. Widow prevention (optional)

## Supported languages

See `references/language-codes.md` for the full list with quote styles and WordPress locale mappings.

## Failure modes

- **Python not found:** Linter requires Python 3.8+. No external dependencies.
- **Unsupported language:** Linter raises `ValueError` with the list of supported codes.
- **Encoding issues:** All files must be UTF-8. The linter applies NFC normalization in Phase 2.
- **Schema/linter mismatch:** The YAML schema is the source of truth. If the linter disagrees, fix the linter.
