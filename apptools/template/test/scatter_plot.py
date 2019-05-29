#-------------------------------------------------------------------------------
#
#  A simple scatter-plot template defined as a test for the template package.
#
#  Written by: David C. Morrill
#  (based on the original cp.plot geo_scatter_plot.py file)
#
#  Date: 07/30/2007
#
#  (c) Copy 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A simple scatter-plot template defined as a test for the template package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Undefined

from traitsui.api \
    import View, VGroup, Item, Label, Theme, TextEditor

from traitsui.wx.themed_slider_editor \
    import ThemedSliderEditor

from traitsui.wx.themed_text_editor \
    import ThemedTextEditor

from chaco.api \
    import ScatterPlot, ArrayPlotData, Plot

from chaco.tools.api \
    import PanTool, SimpleZoom

from enable.api \
    import ColorTrait

from chaco.scatter_markers \
    import marker_trait

from apptools.template.api \
    import Template, TRange, TStr, TDerived, TDataSource

from apptools.template.impl.api \
    import TemplateDataSource, ValueDataNameItem

from .enable_editor \
    import EnableEditor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Template color trait:
TColor = ColorTrait( template = 'copy' )

#-------------------------------------------------------------------------------
#  'ScatterPlot' class:
#-------------------------------------------------------------------------------

class ScatterPlot ( Template ):

    #-- Template Traits --------------------------------------------------------

    # The plot index data source:
    index = TDataSource

    # The plot value data source:
    value = TDataSource

    # The title of the plot:
    title = TStr( 'Scatter Plot' )

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys:
    marker = marker_trait( template = 'copy', event = 'update' )

    # The pixel size of the marker (doesn't include the thickness of the
    # outline):
    marker_size = TRange( 1, 5, 1, event = 'update' )

    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline will be drawn.
    line_width = TRange( 0.0, 5.0, 1.0 )

    # The fill color of the marker:
    color = TColor( 'red', event = 'update' )

    # The color of the outline to draw around the marker
    outline_color = TColor( 'black', event = 'update' )

    #-- Derived Traits ---------------------------------------------------------

    plot = TDerived # Instance( ScatterPlot )

    #-- Traits UI Views --------------------------------------------------------

    # The scatter plot view:
    template_view = View(
        VGroup(
            Item( 'title',
                  show_label = False,
                  style      = 'readonly',
                  editor     = ThemedTextEditor(
                                 theme = Theme( '@GBB', alignment = 'center' ) )
            ),
            Item( 'plot',
                  show_label = False,
                  resizable  = True,
                  editor     = EnableEditor(),
                  item_theme = Theme( '@GF5', margins = 0 )
            )
        ),
        resizable = True
    )

    # The scatter plot options view:
    options_view = View(
        VGroup(
            VGroup(
                Label( 'Scatter Plot Options',
                       item_theme = Theme( '@GBB', alignment = 'center' ) ),
                show_labels = False
            ),
            VGroup(
                Item( 'title', editor = TextEditor() ),
                Item( 'marker' ),
                Item( 'marker_size', editor = ThemedSliderEditor() ),
                Item( 'line_width',
                      label  = 'Line Width',
                      editor = ThemedSliderEditor() ),
                Item( 'color',         label = 'Fill Color' ),
                Item( 'outline_color', label = 'Outline Color' ),
                group_theme = Theme( '@GF5', margins = ( -5, -1 ) ),
                item_theme  = Theme( '@G0B', margins = 0 )
            )
        )
    )

    #-- Default Values ---------------------------------------------------------

    def _index_default ( self ):
        """ Returns the default value for the 'index' trait.
        """
        return TemplateDataSource(
                   items       = [ ValueDataNameItem( name    = 'index',
                                                      flatten = True ) ],
                   description = 'Scatter Plot Index' )

    def _value_default ( self ):
        """ Returns the default value for the 'value' trait.
        """
        return TemplateDataSource(
                   items       = [ ValueDataNameItem( name    = 'value',
                                                      flatten = True ) ],
                   description = 'Scatter Plot Value' )

    #-- ITemplate Interface Implementation -------------------------------------

    def activate_template ( self ):
        """ Converts all contained 'TDerived' objects to real objects using the
            template traits of the object. This method must be overridden in
            subclasses.

            Returns
            -------
            None
        """
        # If our data sources are still unbound, then just exit; someone must
        # have marked them as optional:
        if ((self.index.context_data is Undefined) or
            (self.value.context_data is Undefined)):
            return

        # Create a plot data object and give it this data:
        pd = ArrayPlotData()
        pd.set_data( 'index', self.index.context_data )
        pd.set_data( 'value', self.value.context_data )

        # Create the plot:
        self.plot = plot = Plot( pd )
        plot.plot(      ( 'index', 'value' ),
                        type           = 'scatter',
                        index_sort     = 'ascending',
                        marker         = self.marker,
                        color          = self.color,
                        outline_color  = self.outline_color,
                        marker_size    = self.marker_size,
                        line_width     = self.line_width,
                        bgcolor        = 'white' )
        plot.trait_set( padding_left   = 50,
                        padding_right  = 0,
                        padding_top    = 0,
                        padding_bottom = 20 )

        # Attach some tools to the plot:
        plot.tools.append( PanTool( plot, constrain_key = 'shift' ) )
        zoom = SimpleZoom( component = plot, tool_mode = 'box',
                           always_on = False )
        plot.overlays.append( zoom )

    #-- Trait Event Handlers ---------------------------------------------------

    def _update_changed ( self ):
        """ Handles a plot option being changed.
        """
        self.plot = Undefined

