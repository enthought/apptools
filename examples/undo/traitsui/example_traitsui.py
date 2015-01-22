#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
This is a quick example of showing how to use the undo handler with a Traits
UI embedded in a tasks application.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Enthought standard library imports
from traits.api import HasTraits, Str
from traitsui.api import (Action, Item, Menu, MenuBar, TextEditor, UItem,
                          VGroup, View)

# local library imports
from apptools.undo.api import AbstractCommand, CommandStack, UndoManager
from apptools.undo.traitsui.api import RedoAction, UndoAction, UndoHandler


# simple traits UI action
encode_action = Action(name='Encode', action='do_encode')


class Message(HasTraits):
    """ The model we are editing """

    sender = Str('Bob')

    recipient = Str('Alice')

    message = Str

    # default traitsUI view
    view = View(
        VGroup(
            Item('sender'),
            Item('recipient'),
        ),
        UItem('message', editor=TextEditor(multi_line=True), style='custom'),
        menubar=MenuBar(
            Menu(
                UndoAction,
                RedoAction,
                name='Edit',
            ),
            Menu(
                encode_action,
                name='Encode'
            ),
        ),
        resizable=True,
        height=400, width=600,
    )


class EncodeCommand(AbstractCommand):
    """ Command which encodes trait value in Rot13 """

    name = 'Encoding'

    trait_name = Str('message')

    encoding = Str('rot-13')

    def do(self):
        self.redo()

    def redo(self):
        value = getattr(self.data, self.trait_name)
        setattr(self.data, self.trait_name, value.encode(self.encoding))

    def undo(self):
        value = getattr(self.data, self.trait_name)
        setattr(self.data, self.trait_name, value.decode(self.encoding))


class MessageHandler(UndoHandler):
    """ Handler subclass for Message view """

    def do_encode(self, info):
        """ Action handler that creates a command on the command stack """
        command = EncodeCommand(data=info.object, trait_name='message')
        self.command_stack.push(command)


if __name__ == '__main__':

    message = Message()

    command_stack = CommandStack(undo_manager=UndoManager())
    handler = MessageHandler(command_stack=command_stack)

    message.configure_traits(handler=handler)
