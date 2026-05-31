=== Typeproof ===
Contributors: jbordignon
Tags: typography, quotes, dashes, unicode, i18n, linting
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
Stable tag: 0.1.0
License: GPL-2.0-or-later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Language-aware typographic correction for WordPress. Fixes quotes, dashes, spacing, diacritics, and 50+ Unicode-level rules across 20+ languages.

== Description ==

Typeproof brings professional-grade typographic correction to WordPress. Unlike the built-in `wptexturize()`, it understands language-specific conventions: French narrow no-break spaces before high punctuation, German low-9 quotation marks, Portuguese guillemets, Romanian comma-below diacritics, and dozens more.

**Features:**

* 50+ deterministic rules covering quotes, dashes, spacing, diacritics, symbols, and more
* 20+ language variants with correct quote styles and spacing conventions
* Block editor sidebar for on-demand checking with visual diff
* Optional auto-correct on post save
* REST API for programmatic access
* Register-sensitive rules (editorial, marketing, UI, literary)
* Zero JavaScript dependencies in the linter itself

**How it works:**

The plugin wraps a Python-based linter (`typeproof.py`) via subprocess. The linter handles all the Unicode-level logic; PHP handles the WordPress integration. This means the linter stays in sync with the upstream project automatically.

**Requirements:**

* Python 3.8+ available on the server
* The `typeproof.py` script (included in the Typeproof repo)

== Installation ==

1. Upload the `typeproof` folder to `/wp-content/plugins/`
2. Activate the plugin
3. Go to Settings > Typeproof
4. Set the path to your Python binary and the `typeproof.py` script
5. Click "Run Test" to verify the connection
6. Open any post in the block editor and look for the Typeproof sidebar

== Changelog ==

= 0.1.0 =
* Initial release
* PHP-Python bridge via proc_open
* REST API endpoints (correct, languages)
* Block editor sidebar panel
* Settings page with test connection
* Auto-correct on save (optional)
* wptexturize disable (configurable)
