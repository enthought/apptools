#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from traits.api import Bool, Event, Instance, Interface, Unicode

# Local imports.
from .i_bind_event import IBindEvent


class IScriptManager(Interface):
    """ The script manager interface.  A script manager is responsible for the
    recording of appropriately annotated user actions as scripts that can be
    executed without user intervention at a later time.  Typically an
    application would have a single script manager.
    """

    #### 'IScriptManager' interface ###########################################

    # This event is fired whenever a scriptable object is bound or unbound.  It
    # is intended to be used by an interactive Python shell to give the
    # advanced user access to the scriptable objects.  If an object is created
    # via a factory then the event is fired when the factory is called, and not
    # when the factory is bound.
    bind_event = Event(IBindEvent)

    # This is set if user actions are being recorded as a script.  It is
    # maintained by the script manager.
    recording = Bool(False)

    # This is the text of the script currently being recorded (or the last
    # recorded script if none is currently being recorded).  It is updated
    # automatically as the user performs actions.
    script = Unicode

    # This event is fired when the recorded script changes.  The value of the
    # event will be the ScriptManager instance.
    script_updated = Event(Instance('apptools.appscripting.api.IScriptManager'))

    ###########################################################################
    # 'IScriptManager' interface.
    ###########################################################################

    def bind(self, obj, name=None, bind_policy='unique', api=None,
            includes=None, excludes=None):
        """ Bind obj to name and make (by default) its public methods and
        traits (ie. those not beginning with an underscore) scriptable.  The
        default value of name is the type of obj with the first character
        forced to lower case.

        bind_policy determines what happens if the name is already bound.  If
        the policy is 'auto' then a numerical suffix will be added to the name,
        if necessary, to make it unique.  If the policy is 'unique' then an
        exception is raised.  If the policy is 'rebind' then the previous
        binding is discarded.  The default is 'unique'

        If api is given then it is a class, or a list of classes, that define
        the attributes that will be made scriptable.

        Otherwise if includes is given it is a list of names of attributes that
        will be made scriptable.

        Otherwise all the public attributes of scripted_type will be made
        scriptable except those in the excludes list.
        """

    def bind_factory(self, factory, name, bind_policy='unique', api=None,
            includes=None, excludes=None):
        """ Bind factory to name.  This does the same as the bind() method
        except that it uses a factory that will be called later on to create
        the object only if the object is needed.

        See the documentation for bind() for a description of the remaining
        arguments.
        """

    def run(self, script):
        """ Run the given script, either a string or a file-like object.
        """

    def run_file(self, file_name):
        """ Run the given script file.
        """

    def start_recording(self):
        """ Start the recording of user actions.  The 'script' trait is cleared
        and all subsequent actions are added to 'script'.  The 'recording'
        trait is updated appropriately.
        """

    def stop_recording(self):
        """ Stop the recording of user actions.  The 'recording' trait is
        updated appropriately.
        """
