#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/18/2009
#
#------------------------------------------------------------------------------

# Standard library imports
import codecs
import os.path
from user import home as USER_HOME_DIRECTORY

# System library imports
from configobj import ConfigObj
from validate import Validator

# ETS imports
from enthought.etsconfig.api import ETSConfig
from enthought.pyface.api import AboutDialog, DirectoryDialog, FileDialog, \
    ImageResource, OK, error
from enthought.pyface.action.api import Group as ActionGroup
from enthought.pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget
from enthought.traits.api import HasTraits, Str, Property, Bool, List, \
    Instance, Dict, Int, Any, Event, Enum, on_trait_change
from enthought.traits.ui.api import View, Group, Item, \
    TabularEditor, ListEditor, TextEditor, CodeEditor, InstanceEditor, \
    HTMLEditor
from enthought.traits.ui.extras.saving import SaveHandler
from enthought.traits.ui.key_bindings import KeyBinding, KeyBindings
from enthought.traits.ui.menu import Action, Menu, MenuBar, ToolBar
from enthought.traits.ui.tabular_adapter import TabularAdapter

# Local imports
from rest_editor_model import ReSTHTMLPair
from file_tree import FileTree
from util import docutils_rest_to_html, docutils_rest_to_latex, \
    sphinx_rest_to_html, rest_to_pdf

# Platform and toolkit dependent imports
if ETSConfig.toolkit != 'qt4':
    raise Exception('The rest editor only supports qt4 as toolkit.')


class DocUtilsWarningAdapter(TabularAdapter):
    columns = [('Line', 'line'), ('Description', 'description')]
    image = Property

    icon_mapping = Dict({ 1:ImageResource('info'),
                          2:ImageResource('warning'),
                          3:ImageResource('error') })

    def _get_image(self):
        if self.item is None or self.column != 1:
            return None
        else:
            return self.icon_mapping.get(self.item.level)


class ReSTHTMLPairHandler(SaveHandler):

    # SaveHandler traits
    wildcard = 'ReST files (*.txt;*.rst)|*.txt;*.rst'
    extension = 'rst'
    allowValidationBypass = True
    autosave = True

    # A reference to the toolkit control that is being used to edit the ReST
    rest_control = Any

    # A reference to the toolkit control which is the text editor
    code_widget = Any

    def init(self, info):
        super(ReSTHTMLPairHandler, self).init(info)
        self.saveObject = info.object.model
        for editor in info.ui._editors:
            if editor.name == 'rest':
                self.rest_control = editor.control
                break

        self.code_widget = None
        for child in self.rest_control.children():
            if isinstance(child, AdvancedCodeWidget):
                self.code_widget = child

        print "code widget", self.code_widget

    def object_model_changed(self, info):
        self.saveObject = info.object.model

    def object__editor_action_changed(self, info):
        action = info.object._editor_action_type
        getattr(self.rest_control, action)()



class ReSTHTMLPairView(HasTraits):

    model = Instance(ReSTHTMLPair)

    # ReST editor related traits
    title = Property(Str, depends_on='model.filepath, model.dirty')
    selected_line = Int
    _editor_action = Event
    _editor_action_type = Enum('undo', 'redo', 'cut', 'copy', 'paste',
                               'selectAll')

    # HTML view related traits
    html = Property(Str, depends_on='model.html')
    base_url = Property(Str, depends_on='model.filepath')

    # Warning related traits
    dclicked_warning = Event
    show_warning_lines = Bool(True)
    warning_lines = Property(List(Int),
                             depends_on='model.warnings, show_warning_lines')

    def source_editor_action(self, action):
        self._editor_action_type = action
        self._editor_action = True

    def trait_view(self, name='default'):
        rest_editor = CodeEditor(lexer='null',
                                 selected_line='selected_line',
                                 auto_scroll=True,
                                 squiggle_lines='warning_lines')

        warning_editor = TabularEditor(editable=False,
                                       adapter=DocUtilsWarningAdapter(),
                                       dclicked='dclicked_warning')

        html_editor = HTMLEditor(open_externally=True,
                                 base_url_name='base_url')

        return View(Group(Group(Item('object.model.rest',
                                     style='custom',
                                     editor=rest_editor),
                                Item('html',
                                     editor=html_editor),
                                id='rest_editor_view.PairView.HorzGroup',
                                show_labels=False,
                                orientation='horizontal', layout='split'),
                          Item('object.model.warnings',
                               height=0.2,
                               editor=warning_editor),
                          id='rest_editor_view.PairView.VertGroup',
                          show_labels=False,
                          orientation='vertical', layout='split'),
                    id='rest_editor_view.PairView',
                    handler=ReSTHTMLPairHandler(),
                    width=800, height=600, resizable=True)

    def _dclicked_warning_changed(self, event):
        if event:
            warning = event.item
            self.selected_line = warning.line

    def _get_base_url(self):
        if self.model.filepath:
            return os.path.dirname(self.model.filepath) + os.path.sep
        else:
            return ""

    def _get_html(self):
        if self.model.html:
            return self.model.html
        else:
            message = "Generating HTML..."
            return "<html><body><p>%s</p></body></html>" % message

    def _get_title(self):
        if self.model.filepath:
            title = os.path.basename(self.model.filepath)
        else:
            title = "Untitled"
        if self.model.dirty:
            title = "*" + title + "*"
        return title

    def _get_warning_lines(self):
        if self.show_warning_lines:
            return [ warning.line for warning in self.model.warnings ]
        else:
            return []


class ReSTHTMLEditorHandler(SaveHandler):

    # SaveHandler traits
    wildcard = 'ReST files (*.txt;*.rst)|*.txt;*.rst'
    extension = 'rst'
    allowValidationBypass = True

    # ReSTHTMLEditorHandler traits
    qt_splitter_state = List

    #-----------------------------------------------------------------
    #  Handler interface
    #-----------------------------------------------------------------

    def init(self, info):
        """ Open an empty document if there are no empty views and set
            selected_file to a sensible default if it is not initialized.
        """
        super(ReSTHTMLEditorHandler, self).init(info)

        if not len(info.object.open_views):
            self.new(info)

        if not info.object.selected_file:
            info.object.selected_file = info.object.root_path

    def close(self, info, is_ok):
        """ Called when the user requests to close the interface. Returns a
            boolean indicating whether the window should be allowed to close.

            Prompt for saving, if necessary, and write out config file.
        """
        if self.promptOnExit:
            for view in info.object.open_views:
                self.saveObject = view.model
                self.savePromptMessage = "%s has unsaved changes. Would you " \
                    "like to save them now?" % view.title
                if not self.promptForSave(info):
                    return False

        # If we're closing, set the dirty flags on all the views to false
        # so that save prompts are not opened again
        for view in info.object.open_views:
            view.model.dirty = False

        info.object.config.write()
        return True

    #-----------------------------------------------------------------
    #  SaveHandler interface
    #-----------------------------------------------------------------

    def save(self, info):
        self.saveObject = info.object.selected_view.model
        super(ReSTHTMLEditorHandler, self).save(info)

    def saveAs(self, info):
        self.saveObject = info.object.selected_view.model
        super(ReSTHTMLEditorHandler, self).saveAs(info)

    #-----------------------------------------------------------------
    #  ReSTHTMLEditorHandler interface
    #-----------------------------------------------------------------

    # File menu

    def new(self, info):
        info.object.new()

    def open(self, info):
        selected = info.object.selected_view
        if selected and selected.model.filepath:
            default_directory = os.path.dirname(selected.model.filepath)
        elif os.path.isdir(info.object.selected_file):
            default_directory = info.object.selected_file
        else:
            default_directory = os.path.dirname(info.object.selected_file)

        dialog = FileDialog(action='open', title='Open ReST File',
                            wildcard=self.wildcard,
                            default_directory=default_directory)
        result = dialog.open()
        if result == OK and os.path.exists(dialog.path):
            info.object.open(dialog.path)

    def close_tab(self, info):
        view = info.object.selected_view
        self.saveObject = view.model
        if self.promptForSave(info):
            self.saveObject.dirty = False
            info.object.open_views.remove(view)

    # Edit menu

    def undo(self, info): self._source_editor_action(info, 'undo')
    def redo(self, info): self._source_editor_action(info, 'redo')
    def cut(self, info): self._source_editor_action(info, 'cut')
    def copy(self, info): self._source_editor_action(info, 'copy')
    def paste(self, info): self._source_editor_action(info, 'paste')
    def select_all(self, info): self._source_editor_action(info, 'selectAll')

    def _source_editor_action(self, info, action):
        if info.object.selected_view:
            info.object.selected_view.source_editor_action(action)

    # View menu

    def toggle_file_browser(self, info):
        root = info.ui.control
        main_window = root.layout().itemAt(0).widget()
        splitter = main_window.layout().itemAt(0).widget()
        sizes = splitter.sizes()
        if sizes[0] == 0:
            if len(self.qt_splitter_state):
                splitter.setSizes(self.qt_splitter_state)
            else:
                splitter.setSizes([sizes[1]/2, sizes[1]/2])
        else:
            self.qt_splitter_state = sizes
            splitter.setSizes([0, sum(sizes)])

    # Preferences menu

    def toggle_sphinx(self, info):
        info.object.use_sphinx = not info.object.use_sphinx

    def change_sphinx_static_path(self, info):
        dialog = DirectoryDialog(action='open', title='Select directory')
        result = dialog.open()
        if result == OK and os.path.exists(dialog.path):
            info.object.sphinx_static_path = dialog.path

    # Convert menu

    def docutils_rst2html(self, info):
        rest = info.object.selected_view.model.rest
        html_filepath = info.object.selected_view.model.html_filepath
        f = open(html_filepath, 'w')
        f.write(docutils_rest_to_html(rest)[0])
        f.close()

    def docutils_rst2latex(self, info):
        rest = info.object.selected_view.model.rest
        filepath = info.object.selected_view.model.filepath

        index = filepath.rfind('.')
        if index != -1:
            filepath = filepath[:index]
        latex_filepath = filepath + '.tex'

        f = open(latex_filepath, 'w')
        f.write(docutils_rest_to_latex(rest)[0])
        f.close()

    def sphinx_rst2html(self, info):
        rest = info.object.selected_view.model.rest
        html_filepath = info.object.selected_view.model.html_filepath
        f = open(html_filepath, 'w')
        f.write(sphinx_rest_to_html(rest)[0])
        f.close()

    def rst2pdf(self, info):
        rest_filepath = info.object.selected_view.model.filepath

        if rest_filepath == '':
            error(info.ui.control,
                  'File must be saved before converting it to pdf.')
            return

        pdf_filepath = None

        index = rest_filepath.rfind('.')
        if index != -1:
            pdf_filepath = rest_filepath[:index] + '.pdf'

        rest_to_pdf(rest_filepath, pdf_filepath)

    # Help menu

    def about(self, info):
        text = 'An editor for reStructured Text documentation.'
        AboutDialog(additions=[text]).open()


class ReSTHTMLEditorView(HasTraits):

    root_path = Str(USER_HOME_DIRECTORY)
    filters = List(['*.rst', '*.txt'])

    selected_file = Str

    open_views = List(ReSTHTMLPairView)
    selected_view = Instance(ReSTHTMLPairView)

    config = Any
    use_sphinx = Bool(False)
    sphinx_static_path = Str

    _tree = Instance(FileTree)

    def __init__(self, **kw):
        super(ReSTHTMLEditorView, self).__init__(**kw)
        spec = ConfigObj()
        spec['use_sphinx'] = 'boolean(default=False)'
        path = os.path.join(ETSConfig.application_data, 'rest_editor.conf')
        self.config = ConfigObj(path, configspec=spec, create_empty=True)
        self.config.validate(Validator(), copy=True)
        self.use_sphinx = self.config['use_sphinx']

    #-----------------------------------------------------------------
    #  HasTraits interface
    #-----------------------------------------------------------------

    def trait_view(self, name='default'):
        file_menu = Menu(ActionGroup(Action(name='New', action='new'),
                                     Action(name='Open', action='open'),
                                     Action(name='Close', action='close_tab')),
                         ActionGroup(Action(name='Save', action='save'),
                                     Action(name='Save As', action='saveAs')),
                         ActionGroup(Action(name='Exit', action='exit')),
                         name='File')
        edit_menu = Menu(ActionGroup(Action(name='Undo', action='undo'),
                                     Action(name='Redo', action='redo')),
                         ActionGroup(Action(name='Cut', action='cut'),
                                     Action(name='Copy', action='copy'),
                                     Action(name='Paste', action='paste')),
                         ActionGroup(Action(name='Select All',
                                            action='select_all')),
                         name='Edit')
        view_menu = Menu(ActionGroup(Action(name='Toggle File Browser',
                                            action='toggle_file_browser')),
                         name='View')
        prefs_menu = Menu(Action(name='Use Sphinx', action='toggle_sphinx',
                                 checked=self.use_sphinx, style='toggle'),
                          Action(name='Set Sphinx resources path...',
                                 action='change_sphinx_static_path'),
                          name='Preferences')
        help_menu = Menu(Action(name='About', action='about'),
                         name='Help')
        convert_menu = Menu(Action(name='Docutils - HTML',
                                   action='docutils_rst2html'),
                            Action(name='Docutils - LaTeX',
                                   action='docutils_rst2latex'),
                            Action(name='Sphinx - HTML',
                                   action='sphinx_rst2html'),
                            Action(name='rst2pdf',
                                   action='rst2pdf'),
                            name='Convert')
        menu_bar = MenuBar(file_menu, edit_menu, view_menu, prefs_menu,
                           convert_menu, help_menu)

        ##################################

        tool_bar = ToolBar(ActionGroup(
                                       Action(name='New', action='new',
                                              tooltip = '',
                                              image = ImageResource('new')),
                                       Action(name='Open', action='open',
                                              tooltip = '',
                                              image = ImageResource('open')),
                                       Action(name='Save', action='save',
                                              tooltip = '',
                                              image = ImageResource('save')),
                                       Action(name='Save As', action='saveAs',
                                              tooltip = '',
                                              image = ImageResource('save-as')),
                                       Action(name='Close', action='close_tab',
                                              tooltip = '',
                                              image = ImageResource('close'))
                                      ),
                           ActionGroup(Action(name='Undo', action='undo',
                                              tooltip = '',
                                              image = ImageResource('undo')),
                                       Action(name='Redo', action='redo',
                                              tooltip = '',
                                              image = ImageResource('redo'))
                                      )
                          )

        ##################################

        key_bindings = KeyBindings(
            KeyBinding(binding1='Ctrl-n', method_name='new'),
            KeyBinding(binding1='Ctrl-o', method_name='open'),
            KeyBinding(binding1='Ctrl-s', method_name='save'),
            KeyBinding(binding1='Ctrl-w', method_name='close_tab'),
            KeyBinding(binding1='Ctrl-q', method_name='exit'),
            # The following are identical to the already set hotkeys in
            # the source editor. We just want them to work regardless of
            # whether the editor has focus.
            KeyBinding(binding1='Ctrl-z', method_name='undo'),
            KeyBinding(binding1='Ctrl-y', method_name='redo'),
            KeyBinding(binding1='Ctrl-x', method_name='cut'),
            KeyBinding(binding1='Ctrl-c', method_name='copy'),
            KeyBinding(binding1='Ctrl-v', method_name='paste'),
            KeyBinding(binding1='Ctrl-a', method_name='select_all'))

        return View(Group(Item('_tree',
                               style='custom',
                               width=0.25,
                               editor=InstanceEditor()),
                          Item('open_views',
                               style='custom',
                               editor=ListEditor(use_notebook=True,
                                                 deletable=True,
                                                 dock_style='tab',
                                                 ui_kind='panel',
                                                 selected='selected_view',
                                                 page_name='.title')),
                          id='vma.rest_editor_view.EditorSplit',
                          orientation='horizontal', layout='split',
                          show_labels=False),
                    id='vma.rest_editor_view.EditorView',
                    handler=ReSTHTMLEditorHandler(),
                    width=1024, height=786, resizable=True,
                    menubar=menu_bar,
                    toolbar = tool_bar,
                    key_bindings=key_bindings,
                    title="reStructured Text Editor")

    #-----------------------------------------------------------------
    #  ReSTHTMLEditorView interface
    #-----------------------------------------------------------------

    def new(self, filepath=''):
        """ Create a new document.
        """
        self.add_pair(ReSTHTMLPair(filepath=filepath))

    def open(self, filepath):
        """ Open the file at 'filepath'. 'filepath' is expected to a valid path.
        """
        # If this file is already open, don't open it again
        for view in self.open_views:
            if filepath == view.model.filepath:
                self.selected_view = view
                return

        fh = codecs.open(filepath, 'r', 'utf-8')

        try:
            pair = ReSTHTMLPair(rest=fh.read(), filepath=filepath)
            pair.dirty = False
            self.add_pair(pair)
        finally:
            fh.close()

    def add_pair(self, model):
        """ Update the model preferences to those in the editor, then add it
            to the views, possibly replacing an existing view.
        """
        model.use_sphinx = self.use_sphinx
        model.sphinx_static_path = self.sphinx_static_path

        open_views = self.open_views
        if (len(open_views) and not open_views[-1].model.rest and
            not open_views[-1].model.filepath):
            # An empty, untitled window can be safely be replaced
            view = open_views[-1]
            view.model = model
        else:
            view = ReSTHTMLPairView(model=model)
            open_views.append(view)
        self.selected_view = view

    #-----------------------------------------------------------------
    #  Protected interface
    #-----------------------------------------------------------------

    def __tree_default(self):
        return FileTree(root_path=self.root_path, filters=self.filters)

    @on_trait_change('_tree.selected')
    def _tree_selection_changed(self):
        self.selected_file = self._tree.selected

    def _selected_file_changed(self):
        if os.path.isfile(self.selected_file):
            self.open(self.selected_file)

    def _use_sphinx_changed(self):
        self.config['use_sphinx'] = self.use_sphinx
        for view in self.open_views:
            view.model.use_sphinx = self.use_sphinx

    def _sphinx_static_path_changed(self):
        for view in self.open_views:
            view.model.sphinx_static_path = self.sphinx_static_path
