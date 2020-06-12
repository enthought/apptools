Default User Manager Data API
=============================

This section provides an overview of the part of the ETS Permissions Framework
API used by developers who want to store a user database in a more secure
location (eg. a remote server) than that provided by the default
implementation.

The API is defined by the default user manager which uses password based
authorisation.  If this API isn't sufficiently flexible, or if another method
of authorisation is used (biometrics for example) then an alternative user
manager should be implemented.

The API is fully defined by the `IUserDatabase interface`_.  This allows user
databases to be implemented that extend the `IUser interface`_ and store
additional user related data.  If the user database is being persisted in
secure storage (eg. a remote RDBMS) then this could be used to store sensitive
data (eg. passwords for external systems) that shouldn't be stored as ordinary
preferences.

In most cases there will be no requirement to store additional user related
data than that defined by ``IUser`` so the supplied `UserDatabase
implementation`_ (which provides all the GUI code required to implement the
`IUserDatabase interface`_) can be used.  The `UserDatabase implementation`_
delegates the access to the user database to an object implementing the
`IUserStorage interface`_.  The default implementation of this interface
stores the user database as a pickle in a local file.


Overview of IUserStorage
------------------------

The `IUserStorage interface`_ defines a number of methods that must be
implemented to read and write to the user database.  The methods are designed
to be implemented using simple SQL statements.

In the event of an error a method must raise the ``UserStorageError``
exception.  The string representation of the exception is used as an error
message that is displayed to the user.


Overview of IUserDatabase
-------------------------

The `IUserDatabase interface`_ defines a set of ``Bool`` traits, all beginning
with ``can_``, that describe the capabilities of a particular implementation.
For example, the ``can_add_user`` trait is set by an implementation if it
supports the ability to add a new user to the database.

Each of these capability traits has a corresponding method which has the same
name except for the ``can_`` prefix.  The method only needs to be implemented
if the corresponding traits is ``True``.  The method, for example
``add_user()`` is called by the user manager to implement the capability.

The interface has two other methods.

The ``bootstrapping()`` method is called by the user manager to determine if
the database is bootstrapping.  Typically this is when the database is empty
and no users have yet been defined.  The permissions framework treats this
situation as a special case and is able to relax the enforcement of permissions
to allow users and permissions to be initially defined.

The ``user_factory()`` method is called by the user manager to create a new
user object, ie. an object that implements the `IUser interface`_.  This allows
an implementation to extend the `IUser interface`_ and store additional user
related data in the object if the ``blob`` trait proves insufficient.


.. _`IUser interface`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/i_user.py
.. _`IUserDatabase interface`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/default/i_user_database.py
.. _`IUserStorage interface`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/default/i_user_storage.py
.. _`UserDatabase implementation`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/default/user_database.py
