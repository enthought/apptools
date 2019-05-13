""" The preferences manager. """


# Enthought library imports.
from traits.api import HasTraits, Instance, List, Property, \
    Any, Bool, Dict
from traitsui.api import Handler, HSplit, Item, TreeEditor
from traitsui.api import TreeNode, View, HTMLEditor
from traitsui.menu import Action

# Local imports.
from .preferences_node import PreferencesNode
from .preferences_page import PreferencesPage

# fixme: This is part of the attempt to allow developers to use non-Traits UI
# preferences pages. It doesn't work yet!
##from widget_editor import WidgetEditor


# A tree editor for preferences nodes.
tree_editor = TreeEditor(
    nodes = [
        TreeNode(
            node_for  = [PreferencesNode],
            auto_open = False,
            children  = 'children',
            label     = 'name',
            rename    = False,
            copy      = False,
            delete    = False,
            insert    = False,
            menu      = None,
        ),
    ],

    editable   = False,
    hide_root  = True,
    selected   = 'selected_node',
    show_icons = False
)


class PreferencesHelpWindow(HasTraits):
    """ Container class to present a view with string info. """

    def traits_view(self):
        """ Default view to show for this class. """
        args = []
        kw_args = {'title' : 'Preferences Page Help',
                   'buttons' : ['OK'],
                   'width' : 800,
                   'height' : 800,
                   'resizable' : True,
                   'id' : 'apptools.preferences.ui.preferences_manager.help'}
        to_show = {}

        for name, trait_obj in self.traits().items():
            if name != 'trait_added' and name != 'trait_modified':
                to_show[name] = trait_obj.help
        for name in to_show:
                args.append(Item(name,
                                 style='readonly',
                                 editor=HTMLEditor()
                                 ))

        view = View(*args, **kw_args)
        return view


class PreferencesManagerHandler(Handler):
    """ The traits UI handler for the preferences manager. """

    model = Instance(HasTraits)

    ###########################################################################
    # 'Handler' interface.
    ###########################################################################

    def apply(self, info):
        """ Handle the **Apply** button being clicked. """

        info.object.apply()
        return

    def init(self, info):
        """ Initialize the controls of a user interface. """

        # Select the first node in the tree (if there is one).
        self._select_first_node(info)

        return super(PreferencesManagerHandler, self).init(info)


    def close(self, info, is_ok):
        """ Close a dialog-based user interface. """

        if is_ok:
            info.object.apply()

        return super(PreferencesManagerHandler, self).close(info, is_ok)


    def preferences_help(self, info):
        """ Custom preferences help panel. The Traits help doesn't work."""
        current_page = self.model.selected_page
        to_show = {}
        for trait_name, trait_obj in current_page.traits().items():
            if hasattr(trait_obj, 'show_help') and trait_obj.show_help:
                to_show[trait_name] = trait_obj.help

        help_obj = PreferencesHelpWindow(**to_show)
        help_obj.edit_traits(kind='livemodal')
        return


    ###########################################################################
    # Private interface.
    ###########################################################################

    def _select_first_node(self, info):
        """ Select the first node in the tree (if there is one). """

        root = info.object.root

        if len(root.children) > 0:
            node = root.children[0]
            info.object.selected_page = node.page

        return


class PreferencesManager(HasTraits):
    """ The preferences manager. """

    # All of the preferences pages known to the manager.
    pages = List(PreferencesPage)

    # The root of the preferences node tree.
    root = Property(Instance(PreferencesNode))

    # The preferences node currently selected in the tree.
    selected_node = Instance(PreferencesNode)

    # The preferences associated with the currently selected preferences node.
    selected_page = Instance(PreferencesPage)

    # Should the custom Info button be shown?  If this is True, then an
    # Info button is shown that pops up a trait view with an HTML entry
    # for each trait of the *selected_page* with the metadata 'show_help'
    # set to True.
    show_help = Bool(False)

    # Should the Apply button be shown?
    show_apply = Bool(False)

    #### Traits UI views ######################################################

    def traits_view(self):
        """ Default traits view for this class. """

        help_action = Action(name = 'Info', action = 'preferences_help')

        buttons = ['OK', 'Cancel']

        if self.show_apply:
            buttons = ['Apply'] + buttons
        if self.show_help:
            buttons = [help_action] + buttons


        # A tree editor for preferences nodes.
        tree_editor = TreeEditor(
            nodes = [
                TreeNode(
                    node_for  = [PreferencesNode],
                    auto_open = False,
                    children  = 'children',
                    label     = 'name',
                    rename    = False,
                    copy      = False,
                    delete    = False,
                    insert    = False,
                    menu      = None,
                ),
            ],
            on_select  = self._selection_changed,
            editable   = False,
            hide_root  = True,
            selected   = 'selected_node',
            show_icons = False
        )

        view = View(
            HSplit(
                Item(
                    name       = 'root',
                    editor     = tree_editor,
                    show_label = False,
                    width      = 250,
                ),

                Item(
                    name       = 'selected_page',
                    #editor     = WidgetEditor(),
                    show_label = False,
                    width      = 450,
                    style      = 'custom',
                ),
            ),

            buttons   = buttons,
            handler   = PreferencesManagerHandler(model=self),
            resizable = True,
            title     = 'Preferences',
            width     = .3,
            height    = .3,
            kind      = 'modal'
        )
        self.selected_page = self.pages[0]
        return view

    ###########################################################################
    # 'PreferencesManager' interface.
    ###########################################################################

    #### Trait properties #####################################################

    def _get_root(self):
        """ Property getter. """

        # Sort the pages by the length of their category path. This makes it
        # easy for us to create the preference hierarchy as we know that all of
        # a node's ancestors will have already been created.
        def sort_key(a):
            # We have the guard because if the category is the empty string
            # then split will still return a list containing one item (and not
            # the empty list).
            if len(a.category) == 0:
                len_a = 0

            else:
                len_a = len(a.category.split('/'))

            return len_a

        self.pages.sort(key=sort_key)

        # Create a corresponding preference node hierarchy (the root of the
        # hierachy is NOT displayed in the preference dialog).
        #
        # fixme: Currently we have to create a dummy page for the root node
        # event though the root does not get shown in the tree!
        root_page = PreferencesPage(name='Root', preferences_path='root')
        root      = PreferencesNode(page=root_page)

        for page in self.pages:
            # Get the page's parent node.
            parent = self._get_parent(root, page)

            # Add a child node representing the page.
            parent.append(PreferencesNode(page=page))

        return root

    #### Trait change handlers ################################################

    def _selection_changed(self, new_selection):
        self.selected_node = new_selection


    def _selected_node_changed(self, new):
        """ Static trait change handler. """
        if self.selected_node:
            self.selected_page = self.selected_node.page

        return

    #### Methods ##############################################################

    def apply(self):
        """ Apply all changes made in the manager. """

        for page in self.pages:
            page.apply()

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_parent(self, root, page):
        """ Return the page's parent preference node. """

        parent = root

        if len(page.category) > 0:
            components = page.category.split('/')
            for component in components:
                parent = parent.lookup(component)

        return parent

#### EOF ######################################################################
