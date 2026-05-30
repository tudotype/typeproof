# Supported Language Codes

## Core languages (13 variants)

| BCP 47 | Language | Primary quotes | Alt quotes | WP locale |
|--------|----------|---------------|------------|-----------|
| `pt-PT` | Portuguese (Portugal) | « » | " " | `pt_PT` |
| `pt-BR` | Portuguese (Brazil) | " " | ' ' | `pt_BR` |
| `en-US` | English (US) | " " | ' ' | `en_US` |
| `en-GB` | English (UK) | ' ' | " " | `en_GB` |
| `fr-FR` | French (France) | « » | " " | `fr_FR` |
| `de-DE` | German (Germany) | „ " | ‚ ' | `de_DE` |
| `it-IT` | Italian | « » | " " | `it_IT` |
| `es-ES` | Spanish (Spain) | « » | " " | `es_ES` |
| `es-MX` | Spanish (Mexico) | " " | ' ' | `es_MX` |
| `nl-NL` | Dutch (Netherlands) | " " | ' ' | `nl_NL` |
| `nl-BE` | Dutch (Belgium) | " " | ' ' | `nl_BE` |
| `ro-RO` | Romanian | „ " | « » | `ro_RO` |
| `sc` | Sardinian | « » | " " | — |

## Extended languages (8 additional)

| BCP 47 | Language | Primary quotes | Alt quotes | WP locale |
|--------|----------|---------------|------------|-----------|
| `sv` | Swedish | " " | ' ' | `sv_SE` |
| `nb` | Norwegian Bokmål | « » | ' ' | `nb_NO` |
| `da` | Danish | „ " | ‚ ' | `da_DK` |
| `fi` | Finnish | " " | ' ' | `fi` |
| `pl` | Polish | „ " | ‚ ' | `pl_PL` |
| `cs` | Czech | „ " | ‚ ' | `cs_CZ` |
| `ca` | Catalan | « » | " " | `ca` |
| `ru` | Russian | « » | „ " | `ru_RU` |

## WordPress locale → BCP 47 mapping

Used by the WordPress plugin to auto-detect language:

```php
$map = [
    'pt_PT' => 'pt-PT',
    'pt_BR' => 'pt-BR',
    'en_US' => 'en-US',
    'en_GB' => 'en-GB',
    'en_AU' => 'en-GB',
    'fr_FR' => 'fr-FR',
    'fr_BE' => 'fr-FR',
    'fr_CA' => 'fr-FR',
    'de_DE' => 'de-DE',
    'de_CH' => 'de-DE',
    'de_AT' => 'de-DE',
    'it_IT' => 'it-IT',
    'es_ES' => 'es-ES',
    'es_MX' => 'es-MX',
    'es_AR' => 'es-ES',
    'es_CL' => 'es-ES',
    'es_CO' => 'es-ES',
    'es_VE' => 'es-ES',
    'nl_NL' => 'nl-NL',
    'nl_BE' => 'nl-BE',
    'ro_RO' => 'ro-RO',
    'sv_SE' => 'sv',
    'nb_NO' => 'nb',
    'da_DK' => 'da',
    'fi'    => 'fi',
    'pl_PL' => 'pl',
    'cs_CZ' => 'cs',
    'ca'    => 'ca',
    'ru_RU' => 'ru',
];
```

## Inheritance tree

```
universal
├── en-US
│   └── en-GB (swaps primary/alt quotes)
├── pt-PT
│   └── pt-BR (swaps guillemets for double curly)
├── fr-FR (NNBSP before high punctuation, capital accents)
├── de-DE (Eszett, low-9 quotes)
├── it-IT (guillemets, apostrophic acute)
├── es-ES (inverted punctuation, guillemets)
│   └── es-MX (double curly quotes)
├── nl-NL
│   └── nl-BE
├── ro-RO (cedilla→comma diacritics)
├── sc (Sardinian, guillemets)
├── sv, nb, da, fi, pl, cs, ca, ru
```
