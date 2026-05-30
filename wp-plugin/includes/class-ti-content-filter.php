<?php
/**
 * Auto-correct typography on content save.
 *
 * Hooks content_save_pre when ti_auto_correct option is enabled.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class TI_Content_Filter {

	/**
	 * Hook the content save filter.
	 */
	public static function init() {
		add_filter( 'content_save_pre', array( __CLASS__, 'filter_content' ), 5 );
	}

	/**
	 * Run the linter on post content before saving.
	 *
	 * @param string $content Post content.
	 * @return string Corrected content, or original on failure.
	 */
	public static function filter_content( $content ) {
		if ( empty( $content ) ) {
			return $content;
		}

		// Skip if this is an autosave or revision.
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
			return $content;
		}

		$linter = new TI_Linter();
		$result = $linter->lint( $content );

		if ( is_wp_error( $result ) || ! is_array( $result ) || ! isset( $result['text'] ) ) {
			return $content;
		}

		return $result['text'];
	}
}
