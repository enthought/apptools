#-------------------------------------------------------------------------------
#
#  A n row x m column scatter-plot template defined as a test for the template
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

""" A n row x m column scatter-plot template defined as a test for the template
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
    import GridPlotContainer, PlotComponent

from chaco.scatter_markers \
    import marker_trait

from apptools.template.api \
    import MutableTemplate, TRange, TStr, TList, TDerived

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
#  'ScatterPlotNM' class:
#-------------------------------------------------------------------------------

class ScatterPlotNM ( MutableTemplate ):

    #-- Template Traits --------------------------------------------------------

    # The title of the plot:
    title = TStr( 'NxM Scatter Plots' )

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

    # The number of rows of plots:
    rows = TRange( 1, 3, 1, event = 'grid' )

    # The number of columns of plots:
    columns = TRange( 1, 5, 1, event = 'grid' )

    # The contained scatter plots:
    scatter_plots = TList( ScatterPlot )

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
                Item( 'color',         label = 'Fill Color' ),
                Item( 'outline_color', label = 'Outline Color' ),
                Item( 'rows',    editor = ThemedSliderEditor() ),
                Item( 'columns', editor = ThemedSliderEditor() ),
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
        plots = []
        i     = 0
        for r in range( self.rows ):
            row = []
            for c in range( self.columns ):
                plot = self.scatter_plots[i].plot
                if plot is None:
                    plot = PlotComponent()
                row.append( plot )
                i += 1
            plots.append( row )

        self.plot = GridPlotContainer( shape = ( self.rows, self.columns ) )
        self.plot.component_grid = plots

    #-- Default Values ---------------------------------------------------------

    def _scatter_plots_default ( self ):
        """ Returns the default value for the scatter plots list.
        """
        plots = []
        for i in range( self.rows * self.columns ):
            plots.append( ScatterPlot() )

        self._update_plots( plots )

        return plots

    #-- Trait Event Handlers ---------------------------------------------------

    def _update_changed ( self, name, old, new ):
        """ Handles a plot option being changed.
        """
        for sp in self.scatter_plots:
            setattr( sp, name, new )

        self.plot = Undefined

    def _grid_changed ( self ):
        """ Handles the grid size being changed.
        """
        n     = self.rows * self.columns
        plots = self.scatter_plots
        if n < len( plots ):
            self.scatter_plots = plots[:n]
        else:
            for j in range( len( plots ), n ):
                plots.append( ScatterPlot() )

        self._update_plots( plots )

        self.template_mutated = True

    #-- Private Methods --------------------------------------------------------

    def _update_plots ( self, plots ):
        """ Update the data sources for all of the current plots.
        """
        index = None
        i     = 0
        for r in range( self.rows ):
            for c in range( self.columns ):
                sp   = plots[i]
                i   += 1
                desc = sp.value.description
                col  = desc.rfind( '[' )
                if col >= 0:
                    desc = desc[:col]
                sp.value.description = '%s[%d,%d]' % ( desc, r, c )
                sp.value.optional    = True

                if index is None:
                    index = sp.index
                    index.description = 'Shared Plot Index'
                    index.optional    = True
                else:
                     sp.index = index

