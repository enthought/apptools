Default Policy Manager Data API
===============================

This section provides an overview of the part of the ETS Permissions Framework
API used by developers who want to store a policy manager's persistent data in
a more secure location (eg. a remote server) than that provided by the
default implementation.

The API is defined by the default policy manager which uses roles to make it
easier to assign permissions to users.  If this API isn't sufficiently
flexible, or if roles are inappropriate, then an alternative policy manager
should be implemented.

The API is fully defined by the `IPolicyStorage interface`_.  The default
implementation of this interface stores the policy database as a pickle in a
local file.


Overview of IPolicyStorage
--------------------------

The `IPolicyStorage interface`_ defines a number of methods that must be
implemented to read and write to the policy database.  The methods are designed
to be implemented using simple SQL statements.

In the event of an error a method must raise the ``PolicyStorageError``
exception.  The string representation of the exception is used as an error
message that is displayed to the user.


.. _`IPolicyStorage interface`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/default/i_policy_storage.py
