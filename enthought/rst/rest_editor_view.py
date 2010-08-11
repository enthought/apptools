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
from PyQt4 import QtGui, Qt

# ETS imports
from enthought.etsconfig.api import ETSConfig

if ETSConfig.toolkit != 'qt4':
    try:
        ETSConfig.toolkit = 'qt4'
    except:
        raise Exception('The rest editor only supports qt4 as toolkit. ' + \
         'Toolkit cannot be set to qt4 because it has already been set to wx.')
    else:
        print 'The rest editor only supports qt4 as toolkit. ' + \
              'Toolkit changed to qt4.'

from enthought.pyface.api import AboutDialog, DirectoryDialog, FileDialog, \
    ImageResource, OK, error
from enthought.pyface.action.api import Group as ActionGroup
from enthought.pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget
from enthought.traits.api import HasTraits, Str, Property, Bool, List, \
    Instance, Dict, Int, Any, Event, Enum, on_trait_change, Font
from enthought.traits.ui.api import View, Group, Item, \
    TabularEditor, ListEditor, CodeEditor, InstanceEditor, \
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
    auto_table_fix = Bool(False)

    # A reference to the toolkit control that is being used to edit the ReST
    rest_control = Any

    # A reference to the toolkit control which is the text editor
    code_widget = Any

    # A reference to the toolkit control which is the html editor
    html_control = Any

    def init(self, info):
        super(ReSTHTMLPairHandler, self).init(info)
        self.saveObject = info.object.model
        for editor in info.ui._editors:
            if editor.name == 'rest':
                self.rest_control = editor.control
            if editor.name == 'html':
                self.html_control = editor.control

        self.code_widget = None
        for child in self.rest_control.children():
            if isinstance(child, AdvancedCodeWidget):
                self.code_widget = child

        self.code_widget.code.keyPressEvent_action = self.keyPressEvent_action

    # We redefine the keyPressEvent_action function in the CodeWidget
    # to call the fix_table function when the user types text in a table
    def keyPressEvent_action(self, event):
        if self.auto_table_fix and event.modifiers() != Qt.Qt.ControlModifier:
            self._fix_table(event.key())

    def object_auto_table_fix_changed(self, info):
        self.auto_table_fix = info.object.auto_table_fix

    def object_model_changed(self, info):
        self.saveObject = info.object.model

    def object__editor_action_changed(self, info):
        action = info.object._editor_action_type
        getattr(self.code_widget.code, action)()

    def object__replace_selection_action_changed(self, info):
        cursor = self.code_widget.code.textCursor()
        if cursor.hasSelection():
            cursor.insertText(info.object._new_selection)
        self.code_widget.code.setTextCursor(cursor)

    def object__increase_selection_action_changed(self, info):
        inc = info.object._increase_selection
        cursor = self.code_widget.code.textCursor()
        selection_length = cursor.selectionEnd() - cursor.selectionStart()

        cursor.setPosition(cursor.selectionStart() - inc, 0)
        cursor.movePosition(19, 1, selection_length + 2 * inc)

        self.code_widget.code.setTextCursor(cursor)

    def object__sync_scrollbar_rst2html_action_changed(self, info):
        rst_scrollbar = self.code_widget.code.verticalScrollBar()
        html_frame = self.html_control.page().mainFrame()

        if rst_scrollbar.maximum() == 0:
            return

        rel_pos = float(rst_scrollbar.value()) / float(rst_scrollbar.maximum())
        new_html_pos = rel_pos * html_frame.scrollBarMaximum(2)

        html_frame.setScrollBarValue(2, new_html_pos)

    def object__sync_scrollbar_html2rst_action_changed(self, info):
        rst_scrollbar = self.code_widget.code.verticalScrollBar()
        html_frame = self.html_control.page().mainFrame()

        if html_frame.scrollBarMaximum(2) == 0:
            return

        rel_pos = float(html_frame.scrollPosition().y()) \
                / float(html_frame.scrollBarMaximum(2))
        new_rst_pos = rel_pos * rst_scrollbar.maximum()

        rst_scrollbar.setSliderPosition(new_rst_pos)

    def object__change_font_action_changed(self, info):
        font = info.object._font
        self.code_widget.code.set_font(font)

    def object__find_action_changed(self, info):
        self.code_widget.enable_find()

    def object__replace_action_changed(self, info):
        self.code_widget.enable_replace()

    def object__get_html_pos_action_changed(self, info):
        html_frame = self.html_control.page().mainFrame()
        info.object._html_pos = html_frame.scrollPosition().y()

    def object__set_html_pos_action_changed(self, info):
        html_frame = self.html_control.page().mainFrame()
        html_frame.setScrollBarValue(2, info.object._html_pos)

    def object__fix_underline_action_changed(self, info):
        line_length = self._get_current_line_length(info)
        underline_char = self._get_underline_char(info)

        if underline_char is not None and line_length > 0:
            self._fix_underline(info, underline_char, line_length)

    def object__fix_overline_action_changed(self, info):
        line_length = self._get_current_line_length(info)
        overline_char = self._get_underline_char(info)

        if overline_char is not None and line_length > 0:
            self._fix_overline(info, overline_char, line_length)

    def _fix_underline(self, info, underline_char, line_length):
        cursor = self.code_widget.code.textCursor()
        old_pos = cursor.position()

        cursor.movePosition(12, 0) # Move down one line.
        cursor.select(1) # Selects the line of text under the cursor.

        cursor.insertText(line_length * underline_char)
        self.code_widget.code.setTextCursor(cursor)

        cursor.setPosition(old_pos)
        self.code_widget.code.setTextCursor(cursor)

    def _fix_overline(self, info, overline_char, line_length):
        cursor = self.code_widget.code.textCursor()
        old_pos = cursor.position()

        cursor.movePosition(2, 0) # Move up one line.
        cursor.select(1) # Selects the line of text under the cursor.

        old_length = len(cursor.selectedText())

        cursor.insertText(line_length * overline_char)
        self.code_widget.code.setTextCursor(cursor)

        cursor.setPosition(old_pos + line_length - old_length)
        self.code_widget.code.setTextCursor(cursor)

    def _get_current_line_length(self, info):
        cursor = self.code_widget.code.textCursor()
        cursor.select(1) # Selects the line of text under the cursor.
        return len(cursor.selectedText())

    def _get_underline_char(self, info):
        allowed_chars = ['=', '-', '`', ':', '.', '\'', '"', '~', '^', '_',
                         '*', '+', '#']
        cursor = self.code_widget.code.textCursor()
        cursor.movePosition(3, 0) # Move to the start of the current line.
        cursor.movePosition(12, 0) # Move down one line.
        cursor.movePosition(19, 1) # Move right one character.
        return cursor.selectedText() if cursor.selectedText() in allowed_chars \
               else None


    # FIXME: This function (and the other below) are all quite buggy and should
    # be redone.
    def _fix_table(self, key):
        cursor = self.code_widget.code.textCursor()

        if not self._cursor_in_table(cursor):
            return

        if Qt.Qt.Key_ydiaeresis >= key >= Qt.Qt.Key_Space:
            old_pos = self._move_end_of_cell(cursor)
            if self._chars_before_cursor(cursor, 2) == '  ':
                cursor.deletePreviousChar()
            else:
                while self._cursor_in_table(cursor):
                    cursor.movePosition(Qt.QTextCursor.Up, 0)
                    if self._cursor_on_border(cursor):
                        cursor.insertText(self._chars_before_cursor(cursor, 1))
                        cursor.movePosition(Qt.QTextCursor.Left, 0)
                    else:
                        cursor.insertText(' ')
                        cursor.movePosition(Qt.QTextCursor.Left, 0)

                cursor = self.code_widget.code.textCursor()
                old_pos = self._move_end_of_cell(cursor)

                while self._cursor_in_table(cursor):
                    cursor.movePosition(Qt.QTextCursor.Down, 0)
                    if self._cursor_on_border(cursor):
                        cursor.insertText(self._chars_before_cursor(cursor, 1))
                        cursor.movePosition(Qt.QTextCursor.Left, 0)
                    else:
                        cursor.insertText(' ')
                        cursor.movePosition(Qt.QTextCursor.Left, 0)

            cursor.setPosition(old_pos)

        elif key == Qt.Qt.Key_Backspace:
            chars_before = self._chars_before_cursor(cursor, 2)
            if chars_before == '| ' or chars_before == '+ ':
                cursor.insertText(' ')
            elif chars_before[1] == '|' or chars_before[1] == '+':
                cursor.insertText(' ')
            elif self._chars_at_cursor(cursor, 1) == '|':
                cursor.movePosition(Qt.QTextCursor.Left, Qt.QTextCursor.MoveAnchor)
                self.code_widget.code.setTextCursor(cursor)
                cursor.insertText(' ')

            else:
                old_pos = self._move_end_of_cell(cursor)
                cursor.insertText(' ')
                cursor.setPosition(old_pos)

        elif key == Qt.Qt.Key_Delete:
            if self._chars_at_cursor(cursor, 1) == '|':
                cursor.movePosition(Qt.QTextCursor.Right, Qt.QTextCursor.MoveAnchor)
                cursor.insertText('|')
                cursor.movePosition(Qt.QTextCursor.Left, Qt.QTextCursor.MoveAnchor)
            elif self._chars_at_cursor(cursor, 1) == '+':
                cursor.movePosition(Qt.QTextCursor.Right, Qt.QTextCursor.MoveAnchor)
                cursor.insertText('+')
                cursor.movePosition(Qt.QTextCursor.Left, Qt.QTextCursor.MoveAnchor)
            elif self._chars_at_cursor(cursor, 1) == ' ' and self._chars_before_cursor(cursor, 1) == '|':
                cursor.insertText(' ')
            else:
                old_pos = self._move_end_of_cell(cursor)
                cursor.insertText(' ')
                cursor.setPosition(old_pos)

        elif key == Qt.Qt.Key_Return:
            old_pos = cursor.position()

            cursor.movePosition(Qt.QTextCursor.StartOfLine, 0)

            if self._chars_at_cursor(cursor, 1) == ' ':
                cursor.movePosition(Qt.QTextCursor.NextWord, 0)

            cursor.movePosition(Qt.QTextCursor.EndOfLine, 1)

            eof_pos = cursor.position()

            line = cursor.selectedText()

            cursor.clearSelection()

            for c in line:
                if c == '|' or c == '+':
                    cursor.insertText('|')
                else:
                    cursor.insertText(' ')

            cursor.setPosition(eof_pos)
            self.code_widget.code.setTextCursor(cursor)

    def _move_end_of_cell(self, cursor):
        old_pos = cursor.position()
        while self._chars_at_cursor(cursor, 1) != '|':
            cursor.movePosition(Qt.QTextCursor.Right, Qt.QTextCursor.MoveAnchor)
            if self._chars_at_cursor(cursor, 1) == '+':
                cursor.movePosition(Qt.QTextCursor.Up, Qt.QTextCursor.MoveAnchor)
                if self._chars_at_cursor(cursor, 1) == '|':
                    cursor.movePosition(Qt.QTextCursor.Down, Qt.QTextCursor.MoveAnchor)
                    break
                cursor.movePosition(Qt.QTextCursor.Down, Qt.QTextCursor.MoveAnchor)
        return old_pos

    def _chars_at_cursor(self, cursor, number_chars):
        cursor.movePosition(19, 1, number_chars)
        chars = cursor.selectedText()
        cursor.movePosition(9, 0, number_chars)
        return chars

    def _chars_before_cursor(self, cursor, number_chars):
        cursor.movePosition(Qt.QTextCursor.Left, 1, number_chars)
        chars = cursor.selectedText()
        cursor.movePosition(Qt.QTextCursor.Right, 0, number_chars)
        return chars

    def _cursor_in_table(self, cursor):
        old_pos = cursor.position()
        cursor.movePosition(Qt.QTextCursor.StartOfLine, 0)

        if self._chars_at_cursor(cursor, 1) == ' ':
            cursor.movePosition(Qt.QTextCursor.NextWord, 0)

        in_table = self._chars_at_cursor(cursor, 1) == '|' or \
                   self._chars_at_cursor(cursor, 1) == '+'
        cursor.setPosition(old_pos)
        return in_table

    def _cursor_on_border(self, cursor):
        old_pos = cursor.position()
        cursor.movePosition(Qt.QTextCursor.StartOfLine, 0)
        if self._chars_at_cursor(cursor, 1) == ' ':
            cursor.movePosition(Qt.QTextCursor.NextWord, 0)
        on_border = self._chars_at_cursor(cursor, 1) == '+'
        cursor.setPosition(old_pos)
        return on_border


class ReSTHTMLPairView(HasTraits):

    model = Instance(ReSTHTMLPair)

    # ReST editor related traits
    title = Property(Str, depends_on='model.filepath, model.dirty')
    selected_line = Int
    selected_text = Str
    selected_start_pos = Int
    selected_end_pos = Int
    _editor_action = Event
    _editor_action_type = Enum('undo', 'redo', 'cut', 'copy', 'paste',
                               'selectAll')

    _new_selection = Str
    _replace_selection_action = Event
    _increase_selection = Int
    _increase_selection_action = Event
    _sync_scrollbar_rst2html_action = Event
    _sync_scrollbar_html2rst_action = Event
    _find_action = Event
    _replace_action = Event
    _change_font_action = Event
    _font = QtGui.QFont()
    sync_on_change = Bool(True)

    _fix_underline_action = Event
    _fix_overline_action = Event

    _fix_table_action = Event

    _html_pos = Int
    _get_html_pos_action = Event
    _set_html_pos_action = Event

    auto_table_fix = Bool(False)

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
        rest_editor = CodeEditor(lexer='rest',
                                 selected_line='selected_line',
                                 auto_scroll=True,
                                 squiggle_lines='warning_lines',
                                 selected_text='selected_text',
                                 selected_start_pos='selected_start_pos',
                                 selected_end_pos='selected_end_pos')

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

    @on_trait_change('model.rest')
    def _save_pos(self):
        self._get_html_pos_action = True

    @on_trait_change('model.rest')
    def _fix_table(self):
        self._fix_table_action = True

    @on_trait_change('model.html')
    def _auto_sync(self):
        if self.sync_on_change:
            self._sync_scrollbar_rst2html_action = True
        else:
            self._set_html_pos_action = True

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

    # Search menu

    def enable_find(self, info):
        info.object.selected_view._find_action = True

    def enable_replace(self, info):
        info.object.selected_view._replace_action = True

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
    def toggle_sync_on_change(self, info):
        info.object.sync_on_change = not info.object.sync_on_change

    def toggle_auto_table_fix(self, info):
        info.object.auto_table_fix = not info.object.auto_table_fix

    def toggle_sphinx(self, info):
        info.object.use_sphinx = not info.object.use_sphinx

    def change_sphinx_static_path(self, info):
        dialog = DirectoryDialog(action='open', title='Select directory')
        result = dialog.open()
        if result == OK and os.path.exists(dialog.path):
            info.object.sphinx_static_path = dialog.path

    def change_font(self, info):
        font, ok = QtGui.QFontDialog().getFont(info.object.default_font)

        if ok:
            info.object.default_font = font
            info.object._save_default_font()
            for view in info.object.open_views:
                view._font = font
                view._change_font_action = True

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

    # Markup functions

    def italic(self, info):
        self._set_inline_markup(info, '*')

    def bold(self, info):
        self._set_inline_markup(info, '**')

    def inline_literal(self, info):
        self._set_inline_markup(info, '``')

    def _set_inline_markup(self, info, markup):
        start_pos = info.object.selected_view.selected_start_pos
        end_pos = info.object.selected_view.selected_end_pos
        selected = info.object.selected_view.selected_text
        rest = info.object.selected_view.model.rest
        length = len(markup)

        # 1. The user selected the text with the markup: remove markup.
        if selected[:length] == markup and selected[-length:] == markup:
            self._modify_selection(info, selected[length:-length])
        # 2. The user selected the text between the markup: remove markup.
        elif rest[start_pos-length:start_pos] == markup and \
             rest[end_pos:end_pos+length] == markup:
            self._increase_selection(info, length)
            self._modify_selection(info, selected)
        # 3. There is no markup: add markup.
        else:
            self._modify_selection(info, markup + selected + markup)

    def fix_underline(self, info):
        info.object.selected_view._fix_underline_action = True

    def fix_under_overline(self, info):
        info.object.selected_view._fix_overline_action = True
        info.object.selected_view._fix_underline_action = True

    def _modify_selection(self, info, new_selection):
        info.object.selected_view._new_selection = new_selection
        info.object.selected_view._replace_selection_action = True

    def _increase_selection(self, info, size):
        info.object.selected_view._increase_selection = size
        info.object.selected_view._increase_selection_action = True

    # Scrollbar synchronization functions

    def sync_scrollbar_rst2html(self, info):
        info.object.selected_view._sync_scrollbar_rst2html_action = True

    def sync_scrollbar_html2rst(self, info):
        info.object.selected_view._sync_scrollbar_html2rst_action = True

class ReSTHTMLEditorView(HasTraits):

    root_path = Str(USER_HOME_DIRECTORY)
    filters = List(['*.rst', '*.txt'])

    selected_file = Str

    open_views = List(ReSTHTMLPairView)
    selected_view = Instance(ReSTHTMLPairView)

    default_font = QtGui.QFont()

    config = Any
    use_sphinx = Bool(False)
    sync_on_change = Bool(True)
    auto_table_fix = Bool(False)
    sphinx_static_path = Str

    _tree = Instance(FileTree)

    def __init__(self, **kw):
        super(ReSTHTMLEditorView, self).__init__(**kw)
        self._load_config()

    def _load_config(self):
        spec = ConfigObj()

        spec['use_sphinx'] = 'boolean(default=False)'
        spec['sync_on_change'] = 'boolean(default=True)'
        spec['font_family'] = 'string(default=Monospace)'
        spec['font_point_size'] = 'integer(default=10)'
        spec['font_weight'] = 'integer(default = 50)'
        spec['font_italic'] = 'boolean(default=False)'

        path = os.path.join(ETSConfig.application_data, 'rest_editor.conf')
        self.config = ConfigObj(path, configspec=spec, create_empty=True)
        self.config.validate(Validator(), copy=True)

        self.use_sphinx = self.config['use_sphinx']
        self.sync_on_change = self.config['sync_on_change']
        self.default_font.setFamily(self.config['font_family'])
        self.default_font.setPointSize(self.config['font_point_size'])
        self.default_font.setWeight(self.config['font_weight'])
        self.default_font.setItalic(self.config['font_italic'])
        self.default_font.setStyleHint(QtGui.QFont.TypeWriter)

    #-----------------------------------------------------------------
    #  HasTraits interface
    #-----------------------------------------------------------------

    def trait_view(self, name='default'):
        file_menu = Menu(ActionGroup(Action(name='New \t Ctrl+N',
                                            action='new'),
                                     Action(name='Open \t Ctrl+O',
                                            action='open'),
                                     Action(name='Close \t Ctrl+W',
                                            action='close_tab')),
                         ActionGroup(Action(name='Save \t Ctrl+S',
                                            action='save'),
                                     Action(name='Save As',
                                            action='saveAs')),
                         ActionGroup(Action(name='Exit \t Ctrl+Q',
                                            action='exit')),
                         name='File')
        edit_menu = Menu(ActionGroup(Action(name='Undo \t Ctrl+Z',
                                            action='undo'),
                                     Action(name='Redo \t Ctrl+Y',
                                            action='redo')),
                         ActionGroup(Action(name='Cut \t Ctrl+X',
                                            action='cut'),
                                     Action(name='Copy \t Ctrl+C',
                                            action='copy'),
                                     Action(name='Paste \t Ctrl+V',
                                            action='paste')),
                         ActionGroup(Action(name='Select All \t Ctrl+A',
                                            action='select_all')),
                         name='Edit')

        search_menu = Menu(ActionGroup(Action(name='Find \t Ctrl+F',
                                              action='enable_find'),
                                       Action(name='Replace \t Ctrl+R',
                                              action='enable_replace')),
                           name='Search')

        view_menu = Menu(ActionGroup(Action(name='Toggle File Browser',
                                            action='toggle_file_browser')),
                         name='View')
        prefs_menu = Menu(Action(name='Sync view on change',
                                 action='toggle_sync_on_change',
                                 checked=self.sync_on_change, style='toggle'),
                          Action(name='Auto fix table',
                                 action='toggle_auto_table_fix',
                                 checked=self.auto_table_fix, style='toggle'),
                          Action(name='Use Sphinx', action='toggle_sphinx',
                                 checked=self.use_sphinx, style='toggle'),
                          Action(name='Set Sphinx resources path...',
                                 action='change_sphinx_static_path'),
                          Action(name='Change font', action='change_font'),
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
        menu_bar = MenuBar(file_menu, edit_menu, search_menu, view_menu,
                           prefs_menu, convert_menu, help_menu)

        ########################################################################

        file_group = ActionGroup(Action(tooltip='New', action='new',
                                        image = ImageResource('new')),
                                 Action(tooltip='Open', action='open',
                                        image = ImageResource('open')),
                                 Action(tooltip='Save', action='save',
                                        image = ImageResource('save')),
                                 Action(tooltip='Save As', action='saveAs',
                                        image = ImageResource('save-as')),
                                 Action(tooltip='Close', action='close_tab',
                                        image = ImageResource('close'))
                                )

        edit_group = ActionGroup(Action(tooltip='Cut', action='cut',
                                        image = ImageResource('cut')),
                                 Action(tooltip='Copy', action='copy',
                                        image = ImageResource('copy')),
                                 Action(tooltip='Paste', action='paste',
                                        image = ImageResource('paste'))
                                )

        undo_group = ActionGroup(Action(tooltip='Undo', action='undo',
                                        image = ImageResource('undo')),
                                 Action(tooltip='Redo', action='redo',
                                        image = ImageResource('redo'))
                                )

        search_group = ActionGroup(Action(tooltip='Find',
                                          action='enable_find',
                                          image = ImageResource('find')),
                                   Action(tooltip='Replace',
                                          action='enable_replace',
                                          image = ImageResource('replace')))

        markup_group = ActionGroup(Action(tooltip='Bold', action='bold',
                                          image = ImageResource('bold')),
                                   Action(tooltip='Italic', action='italic',
                                          image = ImageResource('italic')),
                                   Action(tooltip='Inline Literal',
                                          action='inline_literal',
                                          image = ImageResource('literal')),
                                   Action(tooltip='Fix underline (Ctrl+D)',
                                          action='fix_underline',
                                          image = ImageResource('underline')),
                                   Action(tooltip='Fix underline and overline (Ctrl+Shift+D)',
                                          action='fix_under_overline',
                                          image = ImageResource('under-over'))
                                  )

        sync_group = ActionGroup(Action(tooltip='Sync rst2html',
                                        action='sync_scrollbar_rst2html',
                                        image = ImageResource('sync_rst2html')),
                                 Action(tooltip='Sync html2rst',
                                        action='sync_scrollbar_html2rst',
                                        image = ImageResource('sync_html2rst'))
                                )

        tool_bar = ToolBar(file_group, edit_group, undo_group, search_group,
                           markup_group, sync_group)

        ##################################

        key_bindings = KeyBindings(
            KeyBinding(binding1='Ctrl-n', method_name='new'),
            KeyBinding(binding1='Ctrl-o', method_name='open'),
            KeyBinding(binding1='Ctrl-s', method_name='save'),
            KeyBinding(binding1='Ctrl-w', method_name='close_tab'),
            KeyBinding(binding1='Ctrl-q', method_name='exit'),
            KeyBinding(binding1='Ctrl-d', method_name='fix_underline'),
            KeyBinding(binding1='Ctrl-Shift-d', method_name='fix_under_overline'),
            # The following are identical to the already set hotkeys in
            # the source editor. We just want them to work regardless of
            # whether the editor has focus.
            KeyBinding(binding1='Ctrl-z', method_name='undo'),
            KeyBinding(binding1='Ctrl-y', method_name='redo'),
            KeyBinding(binding1='Ctrl-x', method_name='cut'),
            KeyBinding(binding1='Ctrl-c', method_name='copy'),
            KeyBinding(binding1='Ctrl-v', method_name='paste'),
            KeyBinding(binding1='Ctrl-a', method_name='select_all'),
            KeyBinding(binding1='Ctrl-f', method_name='enable_find'),
            KeyBinding(binding1='Ctrl-r', method_name='enable_replace'))

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

        view.sync_on_change = self.sync_on_change
        view.auto_table_fix = self.auto_table_fix
        # Change the font of the rest editor in the new view to the default font
        view._font = self.default_font
        view._change_font_action = True

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

    def _sync_on_change_changed(self):
        self.config['sync_on_change'] = self.sync_on_change
        for view in self.open_views:
            view.sync_on_change = self.sync_on_change

    def _auto_table_fix_changed(self):
        for view in self.open_views:
            view.auto_table_fix = self.auto_table_fix

    def _use_sphinx_changed(self):
        self.config['use_sphinx'] = self.use_sphinx
        for view in self.open_views:
            view.model.use_sphinx = self.use_sphinx

    def _sphinx_static_path_changed(self):
        for view in self.open_views:
            view.model.sphinx_static_path = self.sphinx_static_path

    def _save_default_font(self):
        self.config['font_family'] = self.default_font.family()
        self.config['font_point_size'] = self.default_font.pointSize()
        self.config['font_weight'] = self.default_font.weight()
        self.config['font_italic'] = self.default_font.italic()
