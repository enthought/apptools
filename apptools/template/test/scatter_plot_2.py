#-------------------------------------------------------------------------------
#
#  A simple dual scatter-plot template defined as a test for the template
#  package.
#
#  Written by: David C. Morrill
#  (based on the original cp.plot geo_scatter_plot.py file)
#
#  Date: 08/01/2007
#
#  (c) Copy 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A simple dual scatter-plot template defined as a test for the template
    package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Undefined

from traitsui.api \
    import View, VGroup, Item, Label, Theme, TextEditor

from traitsui.wx.themed_slider_editor \
    import ThemedSliderEditor

from traitsui.wx.themed_text_editor \
    import ThemedTextEditor

from enable.api \
    import ColorTrait

from chaco.api \
    import HPlotContainer

from chaco.scatter_markers \
    import marker_trait

from apptools.template.api \
    import Template, TRange, TStr, TInstance, TDerived

from .enable_editor \
    import EnableEditor

from .scatter_plot \
    import ScatterPlot

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Template color trait:
TColor = ColorTrait( template = 'copy' )

#-------------------------------------------------------------------------------
#  'ScatterPlot2' class:
#-------------------------------------------------------------------------------

class ScatterPlot2 ( Template ):

    #-- Template Traits --------------------------------------------------------

    # The title of the plot:
    title = TStr( 'Dual Scatter Plots' )

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

    # The amount of space between plots:
    spacing = TRange( 0.0, 20.0, 0.0 )

    # The contained scatter plots:
    scatter_plot_1 = TInstance( ScatterPlot, () )
    scatter_plot_2 = TInstance( ScatterPlot, () )

    #-- Derived Traits ---------------------------------------------------------

    plot = TDerived

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
                Item( 'spacing', editor = ThemedSliderEditor() ),
                Item( 'color',         label = 'Fill Color' ),
                Item( 'outline_color', label = 'Outline Color' ),
                group_theme = Theme( '@GF5', margins = ( -5, -1 ) ),
                item_theme  = Theme( '@G0B', margins = 0 )
            )
        )
    )

    #-- ITemplate Interface Implementation -------------------------------------

    def activate_template ( self ):
        """ Converts all contained 'TDerived' objects to real objects using the
            template traits of the object. This method must be overridden in
            subclasses.

            Returns
            -------
            None
        """
        plots = [ p for p in [ self.scatter_plot_1.plot,
                               self.scatter_plot_2.plot ] if p is not None ]
        if len( plots ) == 2:
            self.plot = HPlotContainer( spacing = self.spacing )
            self.plot.add( *plots )
        elif len( plots ) == 1:
            self.plot = plots[0]

    #-- Default Values ---------------------------------------------------------

    def _scatter_plot_1_default ( self ):
        """ Returns the default value for the first scatter plot.
        """
        result = ScatterPlot()
        result.index.description  = 'Shared Plot Index'
        result.value.description += ' 1'

        return result

    def _scatter_plot_2_default ( self ):
        """ Returns the default value for the second scatter plot.
        """
        result = ScatterPlot( index = self.scatter_plot_1.index )
        result.value.description += ' 2'
        result.value.optional = True

        return result

    #-- Trait Event Handlers ---------------------------------------------------

    def _update_changed ( self, name, old, new ):
        """ Handles a plot option being changed.
        """
        setattr( self.scatter_plot_1, name, new )
        setattr( self.scatter_plot_2, name, new )
        self.plot = Undefined

    def _spacing_changed ( self, spacing ):
        """ Handles the spacing between plots being changed.
        """
        self.plot = Undefined

