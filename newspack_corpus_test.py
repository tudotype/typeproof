#!/usr/bin/env python3
"""Newspack publisher corpus test — real journalism from Automattic-hosted sites.

Pulled 2026-04-26 from:
  - Sahan Journal     (en-US)  https://sahanjournal.com
  - Documented        (en-US)  blocked by 403 — skipped
  - El Soberano       (es-MX)  https://elsoberano.mx

Caveat: paragraphs were extracted via WebFetch's summarizer, which may have
normalised some characters. Treat results as directional, not pixel-perfect.
For a true raw test, fetch via WordPress REST `post_content`.
"""
from __future__ import annotations

from typeproof import TypographyLinter


# (locale, register, paragraph)
CORPUS: list[tuple[str, str, str]] = [
    # --- Sahan Journal (en-US, editorial) ---
    ("en-US", "editorial",
     "Since President Donald Trump took office in January 2025, his administration has moved to remake immigration courts across the country and accelerate deportations. More than 100 immigration judges have been fired nationwide, according to the New York Times, while data from courtrooms shows that asylum cases are increasingly being denied."),
    ("en-US", "editorial",
     '"They are looking to, it seems, dispense with these cases in as quick a manner as possible," said Brian Aust, a local immigration attorney.'),
    ("en-US", "editorial",
     "Nationally, asylum grant rates have decreased dramatically since the beginning of Trump's second term. Only 7% of asylum requests were granted in February 2026 nationwide, according to the New York Times, while the Transactional Records Access Clearinghouse (TRAC) puts the number closer to 5%."),
    ("en-US", "editorial",
     "Several local immigration attorneys who spoke with Sahan Journal said the government is increasingly filing motions to deny cases without a full hearing, an action known as pretermission."),
    ("en-US", "editorial",
     "Ryan Wood, a former assistant chief immigration judge in Minnesota who has trained hundreds of immigration judges, said relevant experience is crucial for new judges."),
    ("en-US", "editorial",
     "Fifteen months removed from Trump's inauguration, Wood's concerns about the immigration court system have proven prescient. He said judges are now under immense pressure to accelerate removals, or risk their own positions."),
    ("en-US", "editorial",
     "For Francisco, voluntary departure was not an option. He wanted to stay in the U.S. for his children, he said. But when asked by Miller what relief he was seeking from the court, Francisco's reply was one that for many, there was no longer an answer."),
    ("en-US", "editorial",
     "Burnsville resident Andrea Pedro-Francisco has been in federal immigration detention for more than two months with a life-threatening ovarian cyst that causes her constant pain."),
    ("en-US", "editorial",
     "Pedro-Francisco, 23, was arrested on Feb. 5 while on her way to work, just days before a scheduled surgery to remove the tennis ball-sized cyst. She and her mother are asylum seekers, and immigrated to the United States from Guatemala in 2019."),
    ("en-US", "editorial",
     "According to U.S. Representative Angie Craig: Pedro-Francisco is suffering from pain, bleeding and lightheadedness. She has been taken to an emergency room in Texas, where doctors confirmed she needs surgery."),
    ("en-US", "editorial",
     "Pedro-Francisco has no criminal history and came to the United States at age 16 seeking asylum. She has lived and worked in Minnesota for seven years."),
    ("en-US", "editorial",
     "She is one of about 530 Minnesota detainees who were still held in Texas facilities as of early March, according to Sahan Journal's analysis of U.S. Immigration and Customs Enforcement (ICE) data."),
    ("en-US", "editorial",
     "Mann said she doesn't want to see Pedro-Francisco added to the list of ICE detainees who have died in custody. At least 32 people have died in ICE custody between January 2025 and March 2026, the highest in a single year since the Department of Homeland Security launched in March 2003, according to the New York Times."),

    # --- El Soberano (es-MX, editorial) ---
    ("es-MX", "editorial",
     'El Presidente de Colombia, Gustavo Petro, calificó como "terroristas, fascistas y narcotraficantes" a los responsables del atentado ocurrido en Cajibío, Cauca, que dejó siete civiles muertos y al menos 17 heridos.'),
    ("es-MX", "editorial",
     "A través de su cuenta en la red social X, el Mandatario atribuyó el ataque a grupos armados bajo el mando de alias Marlon, señalando que forman parte de estructuras vinculadas a Iván Mordisco, considerado uno de los criminales más buscados del país y cabecilla del Estado Mayor Central (EMC), principal disidencia de las antiguas FARC."),
    ("es-MX", "editorial",
     'Petro sostuvo que estos grupos son "criminales contra la humanidad" que buscan generar miedo masivo en la población mediante la violencia, con el objetivo de ejercer control territorial y político, en coordinación con actividades del narcotráfico y sectores extremistas.'),
    ("es-MX", "editorial",
     "Ante estos hechos, el jefe de Estado ordenó intensificar la ofensiva contra estas organizaciones, incluyendo el rastreo de sus recursos financieros por parte de la Unidad de Información y Análisis Financiero (UIAF) y el refuerzo del despliegue militar en el departamento del Cauca."),
    ("es-MX", "editorial",
     '"Quiero la máxima persecución mundial contra este grupo narcoterrorista", afirmó el mandatario, quien además anunció que su gobierno avanzará en una denuncia formal ante la Corte Penal Internacional, al considerar que estos actos constituyen crímenes de carácter internacional.'),
]


def show_diff(before: str, after: str) -> str:
    if before == after:
        return "(no change)"
    i = 0
    while i < min(len(before), len(after)) and before[i] == after[i]:
        i += 1
    jb, ja = len(before), len(after)
    while jb > i and ja > i and before[jb - 1] == after[ja - 1]:
        jb -= 1
        ja -= 1
    pad = 30
    cs = max(0, i - pad)
    ceb = min(len(before), jb + pad)
    cea = min(len(after), ja + pad)
    return (
        f"\n  before: …{before[cs:ceb]!r}…"
        f"\n  after : …{after[cs:cea]!r}…"
    )


def main() -> None:
    by_locale: dict[str, list] = {}
    no_change = 0
    changed = 0
    rule_counts: dict[str, int] = {}
    rows = []

    for idx, (locale, register, para) in enumerate(CORPUS, 1):
        linter = TypographyLinter(language=locale, register=register)
        result = linter.lint(para)
        by_locale.setdefault(locale, []).append((idx, para, result))
        if result.text == para:
            no_change += 1
        else:
            changed += 1
            for c in result.corrections:
                rule_counts[c.rule] = rule_counts.get(c.rule, 0) + 1
            rows.append((idx, locale, para, result))

    print(f"Total paragraphs: {len(CORPUS)}")
    print(f"  No change:      {no_change}")
    print(f"  Changed:        {changed}")
    print()
    for locale, entries in by_locale.items():
        nc = sum(1 for _, p, r in entries if r.text == p)
        print(f"  {locale}: {len(entries)} paragraphs, {len(entries)-nc} changed")
    print()
    print("=" * 70)
    print("CHANGED PARAGRAPHS")
    print("=" * 70)
    for idx, locale, original, result in rows:
        rules = sorted({c.rule for c in result.corrections})
        print(f"\n[{idx}] {locale} — rules: {', '.join(rules)} ({len(result.corrections)} edits)")
        print(show_diff(original, result.text))

    print()
    print("=" * 70)
    print("RULE FREQUENCY")
    print("=" * 70)
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        print(f"  {rule:35s} {count}")


if __name__ == "__main__":
    main()
