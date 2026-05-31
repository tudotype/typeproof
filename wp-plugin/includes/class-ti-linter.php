<?php
/**
 * PHP ↔ Python bridge for the Typeproof linter.
 *
 * Calls typeproof.py via proc_open, passing text through stdin
 * and reading structured JSON from stdout.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class TI_Linter {

	/**
	 * WordPress locale → BCP 47 mapping.
	 */
	private static $locale_map = array(
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
	);

	/**
	 * Map a WordPress locale to a BCP 47 code.
	 *
	 * @param string $wp_locale WordPress locale (e.g. 'pt_PT').
	 * @return string|null BCP 47 code or null if unsupported.
	 */
	public static function wp_locale_to_bcp47( $wp_locale ) {
		return self::$locale_map[ $wp_locale ] ?? null;
	}

	/**
	 * Get the configured language, resolving 'auto' to the site locale.
	 *
	 * @return string BCP 47 language code.
	 */
	public static function get_configured_language() {
		$lang = get_option( 'ti_language', 'auto' );

		if ( 'auto' === $lang || empty( $lang ) ) {
			$wp_locale = get_locale();
			$lang      = self::wp_locale_to_bcp47( $wp_locale );
		}

		return $lang ?: 'en-US';
	}

	/**
	 * Lint text through the Python linter.
	 *
	 * @param string      $text     The text to correct.
	 * @param string|null $language BCP 47 language code. Null uses configured default.
	 * @return array|null Parsed JSON result, or null on failure.
	 */
	public function lint( $text, $language = null ) {
		if ( empty( $text ) ) {
			return null;
		}

		$python_path = get_option( 'ti_python_path', 'python3' );
		$linter_path = get_option( 'ti_linter_path', '' );

		if ( empty( $linter_path ) || ! file_exists( $linter_path ) ) {
			return new WP_Error(
				'ti_linter_not_found',
				__( 'Typography linter script not found. Configure the path in Settings → Typeproof.', 'typeproof' )
			);
		}

		if ( null === $language ) {
			$language = self::get_configured_language();
		}

		$register = get_option( 'ti_register', '' );

		// Strip WordPress block comments before sending to Python.
		$block_comments = array();
		$clean_text     = preg_replace_callback(
			'/<!-- wp:.*?-->/',
			function ( $match ) use ( &$block_comments ) {
				$key                  = "\x00WPBLOCK" . count( $block_comments ) . "\x00";
				$block_comments[ $key ] = $match[0];
				return $key;
			},
			$text
		);

		// Build command.
		$cmd = sprintf(
			'%s %s --lang %s --json',
			escapeshellarg( $python_path ),
			escapeshellarg( $linter_path ),
			escapeshellarg( $language )
		);

		if ( ! empty( $register ) ) {
			$cmd .= ' --register ' . escapeshellarg( $register );
		}

		// Run via proc_open with stdin pipe.
		$descriptors = array(
			0 => array( 'pipe', 'r' ), // stdin
			1 => array( 'pipe', 'w' ), // stdout
			2 => array( 'pipe', 'w' ), // stderr
		);

		$process = proc_open( $cmd, $descriptors, $pipes );

		if ( ! is_resource( $process ) ) {
			return new WP_Error(
				'ti_process_failed',
				__( 'Failed to start the typography linter process.', 'typeproof' )
			);
		}

		// Write text to stdin and close.
		fwrite( $pipes[0], $clean_text );
		fclose( $pipes[0] );

		// Read stdout.
		$stdout = stream_get_contents( $pipes[1] );
		fclose( $pipes[1] );

		// Read stderr (for debugging).
		$stderr = stream_get_contents( $pipes[2] );
		fclose( $pipes[2] );

		$exit_code = proc_close( $process );

		if ( 0 !== $exit_code ) {
			return new WP_Error(
				'ti_linter_error',
				sprintf(
					/* translators: 1: exit code, 2: error message */
					__( 'Linter exited with code %1$d: %2$s', 'typeproof' ),
					$exit_code,
					$stderr
				)
			);
		}

		$result = json_decode( $stdout, true );

		if ( null === $result ) {
			return new WP_Error(
				'ti_json_parse_error',
				__( 'Failed to parse linter JSON output.', 'typeproof' )
			);
		}

		// Restore WordPress block comments.
		if ( ! empty( $block_comments ) && isset( $result['text'] ) ) {
			$result['text'] = str_replace(
				array_keys( $block_comments ),
				array_values( $block_comments ),
				$result['text']
			);
		}

		return $result;
	}
}
