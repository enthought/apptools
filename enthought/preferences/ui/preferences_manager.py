""" The preferences manager. """


# Enthought library imports.
from enthought.traits.api import HasTraits, Instance, List, Property
from enthought.traits.ui.api import Handler, HSplit, Item, TreeEditor
from enthought.traits.ui.api import TreeNode, View

# Local imports.
from preferences_node import PreferencesNode
from preferences_page import PreferencesPage
from widget_editor import WidgetEditor


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


class PreferencesManagerHandler(Handler):
    """ The traits UI handler for the preferences manager. """
    
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

    #### Traits UI views ######################################################
    
    view = View(
        HSplit(
            Item(
                name       = 'root',
                editor     = tree_editor,
                show_label = False,
                width      = 200,
            ),

            Item(
                name       = 'selected_page',
                #editor     = WidgetEditor(),
                show_label = False,
                width      = 500
            ),
        ),

        buttons   = ['OK', 'Cancel'],
        handler   = PreferencesManagerHandler(),
        resizable = True,
        style     = 'custom',
        title     = 'Preferences',

        width     = .3,
        height    = .3
    )

    ###########################################################################
    # 'PreferencesManager' interface.
    ###########################################################################

    #### Trait properties #####################################################

    def _get_root(self):
        """ Property getter. """

        # Sort the pages by the length of their category path. This makes it
        # easy for us to create the preference hierarchy as we know that all of
        # a node's ancestors will have already been created.
        def sort(a, b):
            # We have the guard because if the category is the empty string
            # then split will still return a list containing one item (and not
            # the empty list).
            if len(a.category) == 0:
                len_a = 0

            else:
                len_a = len(a.category.split('/'))

            if len(b.category) == 0:
                len_b = 0

            else:
                len_b = len(b.category.split('/'))

            return cmp(len_a, len_b)

        self.pages.sort(sort)
        
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
    
    def _selected_node_changed(self, new):
        """ Static trait change handler. """
        
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
