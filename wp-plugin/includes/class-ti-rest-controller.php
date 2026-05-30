<?php
/**
 * REST API controller for Typography Intelligence.
 *
 * POST /typography-intelligence/v1/correct — lint text
 * GET  /typography-intelligence/v1/languages — supported languages
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class TI_REST_Controller extends WP_REST_Controller {

	protected $namespace = 'typography-intelligence/v1';

	public function register_routes() {
		register_rest_route(
			$this->namespace,
			'/correct',
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => array( $this, 'correct' ),
				'permission_callback' => array( $this, 'check_permission' ),
				'args'                => array(
					'text'     => array(
						'required'          => true,
						'type'              => 'string',
						'sanitize_callback' => function ( $value ) {
							return wp_unslash( $value );
						},
					),
					'language' => array(
						'required' => false,
						'type'     => 'string',
						'default'  => null,
					),
				),
			)
		);

		register_rest_route(
			$this->namespace,
			'/languages',
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => array( $this, 'languages' ),
				'permission_callback' => array( $this, 'check_permission' ),
			)
		);
	}

	/**
	 * Only users who can edit posts may use the linter.
	 */
	public function check_permission() {
		return current_user_can( 'edit_posts' );
	}

	/**
	 * POST /correct — lint the provided text.
	 */
	public function correct( WP_REST_Request $request ) {
		$text     = $request->get_param( 'text' );
		$language = $request->get_param( 'language' );

		$linter = new TI_Linter();
		$result = $linter->lint( $text, $language );

		if ( is_wp_error( $result ) ) {
			return new WP_REST_Response(
				array(
					'error'   => $result->get_error_code(),
					'message' => $result->get_error_message(),
				),
				500
			);
		}

		return new WP_REST_Response( $result, 200 );
	}

	/**
	 * GET /languages — return supported language list.
	 */
	public function languages() {
		$languages = array(
			'pt-PT' => 'Portuguese (Portugal)',
			'pt-BR' => 'Portuguese (Brazil)',
			'en-US' => 'English (US)',
			'en-GB' => 'English (UK)',
			'fr-FR' => 'French (France)',
			'de-DE' => 'German (Germany)',
			'it-IT' => 'Italian',
			'es-ES' => 'Spanish (Spain)',
			'es-MX' => 'Spanish (Mexico)',
			'nl-NL' => 'Dutch (Netherlands)',
			'nl-BE' => 'Dutch (Belgium)',
			'ro-RO' => 'Romanian',
			'sc'    => 'Sardinian',
			'sv'    => 'Swedish',
			'nb'    => 'Norwegian Bokmal',
			'da'    => 'Danish',
			'fi'    => 'Finnish',
			'pl'    => 'Polish',
			'cs'    => 'Czech',
			'ca'    => 'Catalan',
			'ru'    => 'Russian',
		);

		return new WP_REST_Response( $languages, 200 );
	}
}
