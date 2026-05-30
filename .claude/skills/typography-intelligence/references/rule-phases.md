# Linter Pipeline: 8 Phases

The `TypographyLinter.lint()` method runs text through 8 sequential phases. Each phase operates on the output of the previous one. Corrections are tracked with position, original text, replacement, rule name, and description.

## Phase 1: Exclusion masking

Protects regions that must never be modified:

- `<code>`, `<pre>`, `<script>`, `<style>` blocks
- Inline code (backtick-delimited)
- URLs (`http://`, `https://`, `ftp://`)
- File paths (`/path/to/file`, `C:\path`)
- Email addresses
- HTML entities (`&amp;`, `&#x2019;`, etc.)

Replaces each region with a unique placeholder token (`\x00EXCL####\x00`). Restored in Phase 7.

## Phase 2: NFC normalization + zero-width cleanup

- Applies Unicode NFC normalization (canonical decomposition + canonical composition)
- Strips zero-width characters: ZWSP (U+200B), ZWNJ (U+200C), ZWJ (U+200D), word joiner (U+2060), BOM (U+FEFF)

## Phase 3: Language-specific preprocessing

Applies before universal rules, tailored per language:

| Language | Operations |
|----------|-----------|
| `ro-RO` | Cedilla → comma below: Ş→Ș, ş→ș, Ţ→Ț, ţ→ț |
| `fr-FR` | œ/æ ligature restoration, capital accent restoration (É, È, À, Ç, Ù), NNBSP before `;:!?», NBSP after «» |
| `it-IT` | Apostrophic acute: è' → é (perchè→perché, poichè→poiché, etc.) |
| `es-ES/MX` | Inverted punctuation completion (¿...? ¡...!) |
| `es/it/pt` | Capital accent restoration for proper nouns |
| All | Homoglyph detection (Greek β→German ß, Cyrillic lookalikes) |

## Phase 4: Universal substitution rules

Applied to all languages in order:

1. **Ellipsis** — `...` → `…` (U+2026)
2. **Legal symbols** — `(c)` → `©`, `(r)` → `®`, `(tm)` → `™`
3. **Fractions** — `1/2` → `½`, `1/4` → `¼`, `3/4` → `¾`
4. **Primes** — After digits: `'` → `′` (minutes/feet), `"` → `″` (seconds/inches)
5. **Quotation marks** — Straight → curly, language-specific style (see language-codes.md)
6. **Apostrophe** — `'` → `'` (U+2019) in contractions and possessives
7. **Dashes** — `--` → em dash `—` or en dash `–` (context-dependent)
8. **Range dash** — Hyphen in number ranges → en dash (`2020-2025` → `2020–2025`)
9. **Minus sign** — Hyphen before digit → minus `−` (U+2212)
10. **Multiplication** — `x` between digits → `×` (U+00D7)
11. **Double space** — Collapses to single space
12. **Number–unit spacing** — `3m` → `3 m` (thin/narrow space per language)
13. **Percentage spacing** — `25%` → `25 %` or `25%` (language-dependent)
14. **Currency spacing** — Locale-aware: `$10` vs `10 €` vs `10€`
15. **Arrow symbols** — `->` → `→`, `<-` → `←`, `<->` → `↔`

## Phase 4b: Universal structural rules

- **Nested parentheticals** — Correct quote nesting when quotes appear inside parentheses
- **NBSP between initials** — `J. K. Rowling` → `J.\u00a0K.\u00a0Rowling`

## Phase 5: Language-specific post-processing

### 5a: Abbreviations and ordinals

- **en-US/en-GB:** Common abbreviations (Mr., Mrs., Dr., etc.)
- **pt-PT/pt-BR:** Portuguese abbreviations and ordinals (Sr., Sra., 1.º, 2.ª)
- **fr-FR:** French abbreviations (M., Mme, Mlle, n°)
- **es-ES/es-MX:** Spanish ordinals (1.º, 2.ª)
- **de-DE:** Eszett (ß/ẞ), DIN 5008 number formatting

### 5b: NBSP obligations

- After honorific titles (Mr.\u00a0Smith)
- After page abbreviations (p.\u00a012)
- After reference marks (§\u00a05, no.\u00a03)
- After single-letter words (language-specific lists: French à, y, Portuguese e, é, ó)

### 5c: Punctuation rules

- Serial comma (en-US only, register-sensitive)
- Colon capitalization (en-US: capitalize after colon in titles)
- Footnote placement relative to punctuation (varies by language)

## Phase 6: Abbreviation haplology

Prevents double periods when a sentence ends with an abbreviation:

- `He works at Inc..` → `He works at Inc.`
- `The company, Ltd..` → `The company, Ltd.`

## Phase 7: Unmask exclusions

Restores all placeholder tokens from Phase 1 to their original protected content.

## Phase 8: Widow prevention (optional)

Only runs when explicitly enabled (`prevent_widows=True`):

- In paragraphs with 4+ words, replaces the last inter-word space with NBSP
- Prevents a single word from appearing alone on the last line
- Uses language-specific single-letter word lists for additional NBSP insertion
