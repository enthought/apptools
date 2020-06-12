Permissions Framework - Introduction
====================================

The Permissions Framework is a component of the Enthought Tool Suite that
provides developers with the facility to limit access to parts of an
application unless the user is appropriately authorised.  In other words it
enables and disables different parts of the GUI according to the identity of
the user.

The framework includes an API to allow it to be integrated with an
organisation's existing security infrastructure, for example to look users up
in a corporate LDAP directory.

The framework is completely configurable.  Alternate implementations of all
major components can be provided if necessary.  The default implementations
provide a simple local filesystem user database and allows roles to be defined
and assigned to users.

The framework **does not** provide any facility for protecting access to data.
It is not possible to implement such protection in Python and using the file
security provided by a typical operating system.


Framework Concepts
------------------

The following are the concepts supported by the framework.

- Permission

  A permission is the basic tool that a developer uses to specify that access
  to a part of the application should be restricted.  If the current user has
  the permission then access is granted.  A permission may be attached to a
  PyFace action, to an item of a TraitsUI view, or to a GUI toolkit specific
  widget.  When the user is denied access, the corresponding GUI control is
  disabled or completely hidden.

- User

  Each application has a current user who is either *authorised* or
  *unauthorised*.  In order to become authorised a user must identify
  themselves and authenticate that identity.
  
  An arbitrary piece of data (called a blob) can be associated with an
  authorised user which (with user manager support) can be stored securely.
  This might be used, for example, to store sensitive user preferences, or to
  implement a roaming profile.

- User Manager

  The user manager is responsible for authorising the current user and,
  therefore, defines how that is done.  It also provides information about the
  user population to the policy manager.  It may also, optionally, provide the
  ability to manage the user population (eg. add or delete users).  The user
  manager must either maintain a persistent record of the user population, or
  interface with an external user database or directory service.

  The default user manager uses password based authorisation.
  
  The user manager persists its data in a user database.  The default user
  manager provides an API so that different implementations of the user
  database can be used (for example to store the data in an RDBMS, or to
  integrate with an existing directory service).  A default user database is
  provided that pickles the data in a local file.

- Policy Manager

  The policy manager is responsible for assigning permissions to users and for
  determining the permissions assigned to the current user.  To do this it must
  maintain a persistent record of those assignments.

  The default policy manager supplied with the framework uses roles to make it
  easier for an administrator to manage the relationships between permissions
  and users.  A role is defined as a named set of permissions, and a user may
  have one or more roles assigned to them.

  The policy manager persists its data in a policy database.  The default
  policy manager provides an API so that different implementations of the
  policy database can be used (for example to store the data in an RDBMS).  A
  default policy database is provided that pickles the data in a local file.

- Permissions Manager

  The permissions manager is a singleton object used to get and set the current
  policy and user managers.


Framework APIs
--------------

The APIs provided by the permissions framework can be split into the following
groups.

- `Application API`_

  This part of the API is used by application developers.

- `Policy Manager API`_

  This is the interface that an alternative policy manager must implement.  The
  need to implement an alternative is expected to be very rare and so the API
  isn't covered further.  See the definition of the IPolicyManager interface
  for the details.

- `Default Policy Manager Data API`_

  This part of the API is used by developers to store the policy's persistent
  data in a more secure location (eg. on a remote server) than that provided by
  the default implementation.

- `User Manager API`_

  This is the interface that an alternative user manager must implement.  The
  need to implement an alternative is expected to be very rare and so the API
  isn't covered further.  See the definition of the IUserManager interface for
  the details.

- `Default User Manager Data API`_

  This part of the API is used by developers to store the user database in a
  more secure location (eg. on a remote server) than that provided by the
  default implementation.

The complete API_ documentation is available as endo generated HTML.


What Do I Need to Reimplement?
------------------------------

The architecture of the permissions framework comprises several layers, each
of which can reimplemented to meet the requirements of a particular
environment.  Hopefully the following questions and answers will clarify what
needs to be reimplemented depending on your environment.

Q: Do you want to use roles to group permissions and assign them to users?

A: If yes then use the supplied PolicyManager, otherwise provide your own
   IPolicyManager implementation.

Q: Do you want users to be authenticated using a password?

A: If yes then use the supplied UserManager, otherwise provide your own
   IUserManager implementation.

Q: Does the IUser interface allow you to store all the user specific
   information you need?

A: If yes then use the supplied UserDatabase, otherwise provide your own
   IUserDatabase implementation.

Q: Do you want to store your user accounts as pickled data in a local file?

A: If yes then use the supplied default, otherwise provide UserDatabase with
   your own IUserStorage implementation.

Q: Do you want to store your policy data (ie. roles and role assignments) as
   pickled data in a local file?

A: If yes then use the supplied default, otherwise provide PolicyManager with
   your own IPolicyStorage implementation.


Deploying Alternative Managers
------------------------------

The permissions framework will first try to import the different managers from
the ``apptools.permissions.external`` namespace.  The default managers are
only used if no alternative was found.  Therefore, alternative managers should
be deployed as an egg containing that namespace.

Specifically the framework looks for the following classes:

    ``PolicyManager`` from ``apptools.permissions.external.policy_manager``

    ``PolicyStorage`` from ``apptools.permissions.external.policy_storage``

    ``UserDatabase`` from ``apptools.permissions.external.user_database``

    ``UserManager`` from ``apptools.permissions.external.user_manager``

    ``UserStorage`` from ``apptools.permissions.external.user_storage``

The example server is such a package that provides PolicyStorage and
UserStorage implementations that use an XML-RPC based server to provide remote
(and consequently more secure) policy and user databases.


Using the Default Storage Implementations
-----------------------------------------

The default policy and user managers both (again by default) persist their data
as pickles in local files called ``ets_perms_policydb`` and
``ets_perms_userdb`` respectively.  By default these are stored in the
application's home directory (ie. that returned by
``ETSConfig.application_home``).

Note that this directory is normally in the user's own directory structure
whereas it needs to be available to all users of the application.

If the ``ETS_PERMS_DATA_DIR`` environment variable is set then its value is
used instead.

The directory must be writeable by all users of the application.

It should be restated that the default implementations do *not* provide secure
access to the permissions and user data.  They are useful in a cooperative
environment and as working examples.


.. _API: api/index.html
.. _`Application API`: ApplicationAPI.html
.. _`Policy Manager API`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/i_policy_manager.py
.. _`Default Policy Manager Data API`: DefaultPolicyManagerDataAPI.html
.. _`User Manager API`: https://svn.enthought.com/enthought/browser/AppTools/trunk/enthought/permissions/i_user_manager.py
.. _`Default User Manager Data API`: DefaultUserManagerDataAPI.html
