<?php
/**
 * Settings page for Typeproof.
 *
 * Registered under Settings → Typeproof.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class TI_Settings {

	/**
	 * Register settings and fields.
	 */
	public static function register() {
		register_setting( 'ti_settings', 'ti_python_path', array(
			'type'              => 'string',
			'sanitize_callback' => 'sanitize_text_field',
			'default'           => 'python3',
		) );

		register_setting( 'ti_settings', 'ti_linter_path', array(
			'type'              => 'string',
			'sanitize_callback' => 'sanitize_text_field',
			'default'           => '',
		) );

		register_setting( 'ti_settings', 'ti_language', array(
			'type'              => 'string',
			'sanitize_callback' => 'sanitize_text_field',
			'default'           => 'auto',
		) );

		register_setting( 'ti_settings', 'ti_register', array(
			'type'              => 'string',
			'sanitize_callback' => 'sanitize_text_field',
			'default'           => '',
		) );

		register_setting( 'ti_settings', 'ti_auto_correct', array(
			'type'              => 'boolean',
			'sanitize_callback' => 'rest_sanitize_boolean',
			'default'           => false,
		) );

		register_setting( 'ti_settings', 'ti_disable_wptexturize', array(
			'type'              => 'boolean',
			'sanitize_callback' => 'rest_sanitize_boolean',
			'default'           => true,
		) );

		// Section.
		add_settings_section(
			'ti_main',
			__( 'Linter Configuration', 'typeproof' ),
			null,
			'typeproof'
		);

		// Fields.
		add_settings_field( 'ti_python_path', __( 'Python path', 'typeproof' ), array( __CLASS__, 'field_python_path' ), 'typeproof', 'ti_main' );
		add_settings_field( 'ti_linter_path', __( 'Linter script path', 'typeproof' ), array( __CLASS__, 'field_linter_path' ), 'typeproof', 'ti_main' );
		add_settings_field( 'ti_language', __( 'Language', 'typeproof' ), array( __CLASS__, 'field_language' ), 'typeproof', 'ti_main' );
		add_settings_field( 'ti_register', __( 'Register', 'typeproof' ), array( __CLASS__, 'field_register' ), 'typeproof', 'ti_main' );
		add_settings_field( 'ti_auto_correct', __( 'Auto-correct on save', 'typeproof' ), array( __CLASS__, 'field_auto_correct' ), 'typeproof', 'ti_main' );
		add_settings_field( 'ti_disable_wptexturize', __( 'Disable wptexturize', 'typeproof' ), array( __CLASS__, 'field_disable_wptexturize' ), 'typeproof', 'ti_main' );
	}

	public static function field_python_path() {
		$value = get_option( 'ti_python_path', 'python3' );
		printf(
			'<input type="text" name="ti_python_path" value="%s" class="regular-text" /><p class="description">%s</p>',
			esc_attr( $value ),
			esc_html__( 'Path to the Python 3 binary (e.g. python3, /usr/bin/python3).', 'typeproof' )
		);
	}

	public static function field_linter_path() {
		$value = get_option( 'ti_linter_path', '' );
		printf(
			'<input type="text" name="ti_linter_path" value="%s" class="regular-text code" /><p class="description">%s</p>',
			esc_attr( $value ),
			esc_html__( 'Absolute path to typeproof.py.', 'typeproof' )
		);
	}

	public static function field_language() {
		$value    = get_option( 'ti_language', 'auto' );
		$options  = array(
			'auto'  => __( 'Auto (from site locale)', 'typeproof' ),
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

		echo '<select name="ti_language">';
		foreach ( $options as $code => $label ) {
			printf(
				'<option value="%s" %s>%s</option>',
				esc_attr( $code ),
				selected( $value, $code, false ),
				esc_html( $label )
			);
		}
		echo '</select>';
	}

	public static function field_register() {
		$value   = get_option( 'ti_register', '' );
		$options = array(
			''          => __( 'None (default)', 'typeproof' ),
			'editorial' => 'Editorial',
			'marketing' => 'Marketing',
			'ui'        => 'UI',
			'literary'  => 'Literary',
		);

		echo '<select name="ti_register">';
		foreach ( $options as $code => $label ) {
			printf(
				'<option value="%s" %s>%s</option>',
				esc_attr( $code ),
				selected( $value, $code, false ),
				esc_html( $label )
			);
		}
		echo '</select>';
		printf( '<p class="description">%s</p>', esc_html__( 'Register-sensitive rules adjust behavior based on context.', 'typeproof' ) );
	}

	public static function field_auto_correct() {
		$value = get_option( 'ti_auto_correct', false );
		printf(
			'<label><input type="checkbox" name="ti_auto_correct" value="1" %s /> %s</label>',
			checked( $value, true, false ),
			esc_html__( 'Automatically correct typography when posts are saved.', 'typeproof' )
		);
	}

	public static function field_disable_wptexturize() {
		$value = get_option( 'ti_disable_wptexturize', true );
		printf(
			'<label><input type="checkbox" name="ti_disable_wptexturize" value="1" %s /> %s</label><p class="description">%s</p>',
			checked( $value, true, false ),
			esc_html__( 'Disable WordPress built-in smart quotes and dash substitution.', 'typeproof' ),
			esc_html__( 'Recommended. WP texturize conflicts with language-aware rules.', 'typeproof' )
		);
	}

	/**
	 * Render the settings page.
	 */
	public static function render_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		?>
		<div class="wrap ti-settings">
			<h1><?php esc_html_e( 'Typeproof', 'typeproof' ); ?></h1>

			<form method="post" action="options.php">
				<?php
				settings_fields( 'ti_settings' );
				do_settings_sections( 'typeproof' );
				submit_button();
				?>
			</form>

			<hr />

			<h2><?php esc_html_e( 'Test Connection', 'typeproof' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Lint a test string to verify the Python linter is reachable.', 'typeproof' ); ?></p>
			<p>
				<button type="button" class="button" id="ti-test-btn">
					<?php esc_html_e( 'Run Test', 'typeproof' ); ?>
				</button>
			</p>
			<pre id="ti-test-output" style="background:#f5f5f5; padding:12px; margin-top:8px; display:none; white-space:pre-wrap; font-size:13px;"></pre>

			<script>
			document.getElementById('ti-test-btn').addEventListener('click', function() {
				var btn = this;
				var out = document.getElementById('ti-test-output');
				btn.disabled = true;
				btn.textContent = '<?php echo esc_js( __( 'Testing...', 'typeproof' ) ); ?>';
				out.style.display = 'block';
				out.textContent = '';

				wp.apiFetch({
					path: '/typeproof/v1/correct',
					method: 'POST',
					data: { text: 'He said "hello"... It\'s a test -- right?' }
				}).then(function(result) {
					out.textContent = JSON.stringify(result, null, 2);
					btn.disabled = false;
					btn.textContent = '<?php echo esc_js( __( 'Run Test', 'typeproof' ) ); ?>';
				}).catch(function(err) {
					out.textContent = 'Error: ' + (err.message || JSON.stringify(err));
					btn.disabled = false;
					btn.textContent = '<?php echo esc_js( __( 'Run Test', 'typeproof' ) ); ?>';
				});
			});
			</script>
		</div>
		<?php
	}
}
