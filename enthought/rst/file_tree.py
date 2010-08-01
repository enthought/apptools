import os
import glob

from enthought.traits.api import HasTraits, Str, Property, List, \
        Directory, cached_property, Instance
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item

class FileNode(HasTraits):
    path = Str()
    name = Property(Str, depends_on='path')

    def __init__(self, path, *args, **kw):
        self.path = path
        super(FileNode, self).__init__(*args, **kw)

    @cached_property
    def _get_name(self):
        return os.path.split(self.path)[-1]

class DirectoryNode(HasTraits):

    filters = List(Str)
    path = Str()
    children = Property(List, depends_on='path')
    name = Property(Str, depends_on='path')

    def __init__(self, path, *args, **kw):
        self.path = path
        super(DirectoryNode, self).__init__(*args, **kw)

    def _default_filters(self):
        return ['*.*']

    @cached_property
    def _get_name(self):
        return os.path.split(self.path)[-1]

    @cached_property
    def _get_children(self):
        file_paths = []
        for filter in self.filters:
            filter_path = os.path.join(self.path, filter)
            file_paths += os.path.join(glob.glob(filter_path))

        files = [FileNode(path) for path in file_paths]
        files.sort(key=lambda node: node.name.lower())

        dirs = []
        # Pass filenames through str() to convert from unicode.
        names = [str(f) for f in os.listdir(self.path)]
        
        names.sort(key=str.lower)
        for fn in names:
            path = os.path.join(self.path, fn)
            if os.path.isdir(path) and not fn.startswith('.') \
                                   and not self._access_denied(path):
                dirs.append(DirectoryNode(path, filters=self.filters))

        return dirs + files
        
        
    # On Windows 7 (maybe on Vista/XP too, but not tested there) calling 
    # os.listdir() on certain folders raises a "WindowsError: [Error 5] Access 
    # is denied" exception. What we do here, is when populating the list of
    # folders, we check if a folder is accessible by the user before adding it.
    def _access_denied(self, path):
        try:
            os.listdir(path)
            return False
        except WindowsError as win_err:
            # print win_err
            return True

class FileTree(HasTraits):
    root_path = Directory('.')
    filters = List()
    selected = Str()

    _root = Instance(DirectoryNode)

    def traits_view(self, parent=None):
        nodes = [TreeNode(node_for=[FileNode],
                          children='',
                          label='name',
                          view=View()),
                 TreeNode(node_for=[DirectoryNode],
                          children='children',
                          label='name',
                          view=View())]

        return View(Item('root_path', show_label=False),
                    Item('_root',
                         editor=TreeEditor(nodes=nodes,
                                           on_dclick=self._on_dclick,
                                           on_click=self._on_click,
                                           editable=False),
                         show_label=False))

    ###########################################################################
    # initialization methods
    ###########################################################################
    def _filters_default(self):
        return ['*.*']

    def __root_default(self):
        return DirectoryNode(os.path.abspath(self.root_path),
                             filters=self.filters)

    ###########################################################################
    # protected methods
    ###########################################################################

    def _on_dclick(self, node):
        if isinstance(node, DirectoryNode):
            self.root_path = node.path
        if isinstance(node, FileNode):
            self.selected = node.path

    def _on_click(self, node):
        if isinstance(node, FileNode):
            self.selected = node.path

    ###########################################################################
    # traits handlers methods
    ###########################################################################
    def _root_path_changed(self, new):
        if not self.traits_inited():
            return
        self.selected = ''
        self._root = DirectoryNode(os.path.abspath(new), filters=self.filters)
