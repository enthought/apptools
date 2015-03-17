Application API
===============

This section provides an overview of the part of the ETS Permissions Framework
API used by application developers.  The `Permissions Framework example`_
demonstrates the API in use.  An application typically uses the API to do the
following:

- define permissions

- apply permissions

- user authentication

- getting and setting user data

- integrate management actions.


Defining Permissions
--------------------

A permission is the object that determines the user's access to a part of an
application.  While it is possible to apply the same permission to more than
one part of an application, it is generally a bad idea to do so as it makes it
difficult to separate them at a later date.

A permission has an id and a human readable description.  Permission ids
must be unique.  By convention a dotted notation is used for ids to give
them a structure.  Ids should at least be given an application or plugin
specific prefix to ensure their uniqueness.

Conventionally all an applications permissions are defined in a single
``permissions.py`` module.  The following is an extract of the example's
``permissions.py`` module::

    from apptools.permissions.api import Permission

    # Add a new person.
    NewPersonPerm = Permission(id='ets.permissions.example.person.new',
            description=u"Add a new person")

    # Update a person's age.
    UpdatePersonAgePerm = Permission(id='ets.permissions.example.person.age.update',
            description=u"Update a person's age")

    # View or update a person's salary.
    PersonSalaryPerm = Permission(id='ets.permissions.example.person.salary',
            description=u"View or update a person's salary")


Applying Permissions
--------------------

Permissions are applied to different parts of an applications GUI.  When the
user has been granted a permission then the corresponding part of the GUI is
displayed normally.  When the user is denied a permission then the
corresponding part of the GUI is disabled or completely hidden.

Permissions can be applied to TraitsUI view items and to any object which can
be wrapped in a ``SecureProxy``.


TraitsUI View Items
...................

Items in TraitsUI views have ``enabled_when`` and ``visible_when`` traits that
are evaluated to determine if the item should be enabled or visible
respectively.  These are used to apply permissions by storing the relevant
permissions in the model so that they are available to the view.  The
``enabled_when`` and ``visible_when`` traits then simply reference the
permission's ``granted`` trait.  The ``granted`` trait automatically reflects
whether or not the user currently has the corresponding permission.

In order for the view to be correctly updated when the user's permissions
change (ie. when they become authenticated) the view must use the
``SecureHandler`` handler.  This handler is a simple sub-class of the standard
Traits ``Handler`` class.

The following extract from the example shows a default view of the ``Person``
object that enables the ``age`` item when the user has the
``UpdatePersonAgePerm`` permission and shows the ``salary`` item when the user
has the ``PersonSalaryPerm`` permission::

    from apptools.permissions.api import SecureHandler
    from traits.api import HasTraits, Int, Unicode
    from traitsui.api import Item, View

    from permissions import UpdatePersonAgePerm, PersonSalaryPerm

    class Person(HasTraits):
        """A simple example of an object model"""

        # Name.
        name = Unicode

        # Age in years.
        age = Int

        # Salary.
        salary = Int

        # Define the default view with permissions attached.
        age_perm = UpdatePersonAgePerm
        salary_perm = PersonSalaryPerm

        traits_view = View(
                Item(name='name'),
                Item(name='age', enabled_when='object.age_perm.granted'),
                Item(name='salary', visible_when='object.salary_perm.granted'),
                handler=SecureHandler)


Wrapping in a SecureProxy
.........................

Any object can have permissions applied by wrapping it in a ``SecureProxy``
object.  An adapter is used that manages the enabled and visible states of the
proxied object according to the current user's permissions.  Otherwise the
proxy behaves just like the object being proxied.

Adapters are included for the following types of object:

- PyFace actions

- PyFace widgets **FIXME:** TODO

- Qt widgets

- wx widgets

See `Writing SecureProxy Adapters`_ for a description of how to write adapters
for other types of objects.

The following extract from the example shows the wrapping of a standard PyFace
action and the application of the ``NewPersonPerm`` permission::

    from apptools.permissions.api import SecureProxy

    from permissions import NewPersonPerm

    ...

        def _new_person_action_default(self):
            """Trait initializer."""

            # Create the action and secure it with the appropriate permission.
            act = Action(name='New Person', on_perform=self._new_person)
            act = SecureProxy(act, permissions=[NewPersonPerm])

            return act

A ``SecureProxy`` also accepts a ``show`` argument that, when set to
``False``, hides the object when it becomes disabled.


Authenticating the User
-----------------------

The user manager supports the concept of the current user and is responsible
for authenticating the user (and subsequently unauthorising the user if
required).

The code fragment to authenticate the current user is::

    from apptools.permissions.api import get_permissions_manager

    get_permissions_Manager().user_manager.authenticate_user()

Unauthorising the current user is done using the ``unauthenticate_user()``
method.

As a convenience two PyFace actions, called ``LoginAction`` and
``LogoutAction``, are provided that wrap these two methods.

As a further convenience a PyFace menu manager, called ``UserMenuManager``, is
provided that contains all the user and management actions (see below) in the
permissions framework.  This is used by the example.

The user menu, login and logout actions can be imported from
``apptools.permissions.action.api``.


Getting and Setting User Data
-----------------------------

The user manager has a ``user`` trait that is an object that implements the
``IUser`` interface.  It is only valid once the user has been authenticated.

The ``IUser`` interface has a ``blob`` trait that holds any binary data (as a
Python string).  The data will be read when the user is authenticated.  The
data will be written whenever it is changed.


Integrating Management Actions
------------------------------

Both policy and user managers can provide actions that provide access to
various management functions.  Both have a ``management_actions`` trait that is
a list of PyFace actions that invoke appropriate dialogs that allow the user to
manage the policy and the user population appropriately.

User managers also have a ``user_actions`` trait that is a list of PyFace
actions that invoke appropriate dialogs that allow the user to manage
themselves.  For example, the default user manager provides an action that
allows a user to change their password.

The default policy manager provides actions that allows roles to be defined in
terms of sets of permissions, and allows users to be assigned one or more
roles.

The default user manager provides actions that allows users to be added,
modified and deleted.  A user manager that integrates with an enterprise's
secure directory service may not provide any management actions.

All management actions have appropriate permissions attached to them.


Writing SecureProxy Adapters
----------------------------

``SecureProxy`` will automatically handle most of the object types you will
want to apply permissions to.  However it is possible to implement additional
adapters to support other object types.  To do this you need to implement a
sub-class of ``AdapterBase`` and register it.

Adapters tend to be one of two styles according to how the object's enabled
and visible states are changed.  If the states are changed via attributes
(typically Traits based objects) then the adapter will cause a proxy to be
created for the object.  If the states are changed via methods (typically
toolkit widgets) then the adapter will probably modify the object itself.  We
will refer to these two styles as wrapping adapters and patching adapters
respectively.

The following gives a brief overview of the ``AdapterBase`` class:

``proxied``
    This instance attribute is a reference to the original object.

``register_adapter(adapter, type, type, ...)``
    This is a class method that is used to register your adapter and one or
    more object types that it handles.

``adapt()``
    This is a method that should be reimplemented by patching adapters.  (The
    default implementation will cause a proxy to be created for wrapping
    adapters.)  This is where any patching of the ``proxied`` attribute is
    done.  The object returned will be returned by ``SecureProxy()`` and would
    normally be the patched object - but can be any object.

``setattr(name, value)``
    This method should be reimplemented by wrapping adapters to intercept the
    setting of relevant attributes of the ``proxied`` object.  The default
    implementation should be used as the fallback for irrelevant attributes.

``get_enabled()``
    This method must be reimplemented to return the current enabled state.

``set_enabled(value)``
    This method must be reimplemented to set the enabled state to the given
    value.

``update_enabled(value)``
    This method is called by your adapter to set the desired value of the
    enabled state.  The actual state set will depend on the current user's
    permissions.

``get_visible()``
    This method must be reimplemented to return the current visible state.

``set_visible(value)``
    This method must be reimplemented to set the visible state to the given
    value.

``update_visible(value)``
    This method is called by your adapter to set the desired value of the
    visible state.  The actual state set will depend on the current user's
    permissions.

The ``AdapterBase`` class is defined in `adapter_base.py`_.

The `PyFace action adapter`_ is an example of a wrapping adapter.

The `PyQt widget adapter`_ is an example of a patching adapter.


.. _`Permissions Framework example`: https://svn.enthought.com/enthought/browser/AppTools/trunk/examples/permissions/application/
.. _`adapter_base.py`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/adapter_base.py
.. _`PyFace action adapter`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/adapters/pyface_action.py
.. _`PyQt widget adapter`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/adapters/qt4_widget.py
