""" An instance editor that allows total control over widget creation. """


# Enthought library imports.
from traits.etsconfig.api import ETSConfig
from traits.api import Any
from traitsui.api import EditorFactory

# fixme: We need to import the 'Editor' class from the appropriate toolkit.
exec('from traitsui.%s.editor import Editor' % ETSConfig.toolkit)


class _WidgetEditor(Editor):
    """ An instance editor that allows total control over widget creation. """

    #### '_WidgetEditor' interface ############################################

    # The toolkit-specific parent of the editor.
    parent = Any

    ###########################################################################
    # '_WidgetEditor' interface.
    ###########################################################################

    def init(self, parent):
        """ Initialize the editor. """

        self.parent = parent

        # fixme: What if there are no pages?!?
        page = self.object.pages[0]

        # Create the editor's control.
        self.control = page.create_control(parent)

        # Listen for the page being changed.
        self.object.on_trait_change(self._on_page_changed, 'selected_page')

        return

    def dispose(self):
        """ Dispose of the editor. """

        page = self.object.selected_page
        page.destroy_control()

        return

    def update_editor(self):
        """ Update the editor. """

        pass

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _on_page_changed(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        if old is not None:
            old.destroy_control()

        if new is not None:
            self.control = new.create_control(self.parent)

        return


class WidgetEditor(EditorFactory):
    """ A factory widget editors. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __call__ (self, *args, **traits):
        """ Call the object. """

        return self.trait_set(**traits)

    ###########################################################################
    # 'EditorFactory' interface.
    ###########################################################################

    def simple_editor(self, ui, object, name, description, parent):
        """ Create a simple editor. """

        editor = _WidgetEditor(
            parent,
            factory     = self,
            ui          = ui,
            object      = object,
            name        = name,
            description = description
        )

        return editor

    custom_editor   = simple_editor
    text_editor     = simple_editor
    readonly_editor = simple_editor

#### EOF ######################################################################
