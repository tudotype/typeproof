( function( wp ) {
	var registerPlugin = wp.plugins.registerPlugin;
	var PluginSidebar  = wp.editPost.PluginSidebar;
	var el             = wp.element.createElement;
	var useState       = wp.element.useState;
	var useSelect      = wp.data.useSelect;
	var useDispatch    = wp.data.useDispatch;
	var Button         = wp.components.Button;
	var PanelBody      = wp.components.PanelBody;
	var Spinner        = wp.components.Spinner;
	var apiFetch       = wp.apiFetch;
	var __              = wp.i18n.__;

	/**
	 * Extract plain text from all blocks in the editor.
	 */
	function getBlockText( blocks ) {
		var text = '';
		blocks.forEach( function( block ) {
			if ( block.attributes && block.attributes.content ) {
				// Strip HTML tags for plain text extraction.
				var div = document.createElement( 'div' );
				div.innerHTML = block.attributes.content;
				text += div.textContent + '\n\n';
			}
			if ( block.innerBlocks && block.innerBlocks.length ) {
				text += getBlockText( block.innerBlocks );
			}
		} );
		return text;
	}

	/**
	 * Apply corrections back to blocks by replacing content.
	 */
	function applyToBlocks( blocks, original, corrected, editBlock ) {
		blocks.forEach( function( block ) {
			if ( block.attributes && block.attributes.content ) {
				var div = document.createElement( 'div' );
				div.innerHTML = block.attributes.content;
				var blockText = div.textContent;

				// Find this block's text range in the original.
				var startIdx = original.indexOf( blockText );
				if ( startIdx !== -1 ) {
					var endIdx       = startIdx + blockText.length;
					var correctedSub = corrected.substring( startIdx, endIdx );

					if ( correctedSub !== blockText ) {
						// Rebuild the HTML with corrected text.
						var newContent = block.attributes.content;

						// Apply character-level replacements to preserve HTML.
						var textNodes = [];
						var walker    = document.createTreeWalker(
							div,
							NodeFilter.SHOW_TEXT,
							null,
							false
						);
						while ( walker.nextNode() ) {
							textNodes.push( walker.currentNode );
						}

						var offset = 0;
						textNodes.forEach( function( node ) {
							var nodeLen      = node.textContent.length;
							var correctedPart = correctedSub.substring( offset, offset + nodeLen );
							if ( node.textContent !== correctedPart ) {
								node.textContent = correctedPart;
							}
							offset += nodeLen;
						} );

						newContent = div.innerHTML;
						editBlock( block.clientId, { content: newContent } );
					}
				}
			}
			if ( block.innerBlocks && block.innerBlocks.length ) {
				applyToBlocks( block.innerBlocks, original, corrected, editBlock );
			}
		} );
	}

	function TISidebar() {
		var blocks = useSelect( function( select ) {
			return select( 'core/block-editor' ).getBlocks();
		}, [] );

		var editBlock = useDispatch( 'core/block-editor' ).updateBlockAttributes;

		var state       = useState( null );
		var result      = state[0];
		var setResult   = state[1];

		var loadState   = useState( false );
		var loading     = loadState[0];
		var setLoading  = loadState[1];

		var errState    = useState( null );
		var error       = errState[0];
		var setError    = errState[1];

		var appliedState  = useState( false );
		var applied       = appliedState[0];
		var setApplied    = appliedState[1];

		function checkTypography() {
			var text = getBlockText( blocks ).trim();
			if ( ! text ) {
				setError( __( 'No text content found.', 'typography-intelligence' ) );
				return;
			}

			setLoading( true );
			setError( null );
			setResult( null );
			setApplied( false );

			apiFetch( {
				path: '/typography-intelligence/v1/correct',
				method: 'POST',
				data: {
					text: text,
					language: window.tiSettings ? window.tiSettings.language : null,
				},
			} ).then( function( res ) {
				setResult( res );
				setLoading( false );
			} ).catch( function( err ) {
				setError( err.message || __( 'Linter request failed.', 'typography-intelligence' ) );
				setLoading( false );
			} );
		}

		function applyCorrections() {
			if ( ! result || ! result.text ) return;

			var originalText = getBlockText( blocks ).trim();
			applyToBlocks( blocks, originalText, result.text, editBlock );
			setApplied( true );
		}

		// Build corrections list.
		var correctionElements = [];
		if ( result && result.corrections && result.corrections.length ) {
			correctionElements = result.corrections.map( function( c, i ) {
				return el( 'div', { key: i, className: 'ti-correction' },
					el( 'span', { className: 'ti-correction-rule' }, c.rule ),
					el( 'div', { className: 'ti-correction-detail' },
						el( 'del', null, c.original ),
						' \u2192 ',
						el( 'ins', null, c.replacement )
					),
					c.description ? el( 'p', { className: 'ti-correction-desc' }, c.description ) : null
				);
			} );
		}

		return el( PluginSidebar, {
				name: 'typography-intelligence',
				title: __( 'Typography Intelligence', 'typography-intelligence' ),
				icon: 'editor-spellcheck',
			},
			el( PanelBody, { title: __( 'Check Typography', 'typography-intelligence' ), initialOpen: true },
				el( Button, {
					variant: 'primary',
					onClick: checkTypography,
					disabled: loading,
					style: { width: '100%', justifyContent: 'center' },
				}, loading ? el( Spinner, null ) : __( 'Check Typography', 'typography-intelligence' ) ),

				error ? el( 'div', { className: 'ti-error', style: { marginTop: '12px', color: '#d63638' } }, error ) : null,

				result && result.stats ? el( 'div', { className: 'ti-stats', style: { marginTop: '12px' } },
					el( 'strong', null,
						result.stats.total_corrections === 0
							? __( 'No corrections needed.', 'typography-intelligence' )
							: result.stats.total_corrections + ' ' + __( 'corrections found', 'typography-intelligence' )
					)
				) : null,

				correctionElements.length ? el( 'div', { className: 'ti-corrections', style: { marginTop: '12px' } },
					correctionElements
				) : null,

				result && result.stats && result.stats.total_corrections > 0 && ! applied
					? el( Button, {
						variant: 'secondary',
						onClick: applyCorrections,
						style: { width: '100%', justifyContent: 'center', marginTop: '12px' },
					}, __( 'Apply Corrections', 'typography-intelligence' ) )
					: null,

				applied ? el( 'div', { style: { marginTop: '12px', color: '#00a32a' } },
					__( 'Corrections applied.', 'typography-intelligence' )
				) : null
			)
		);
	}

	registerPlugin( 'typography-intelligence', {
		render: TISidebar,
		icon: 'editor-spellcheck',
	} );
} )( window.wp );
