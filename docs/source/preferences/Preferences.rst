Preferences
===========

The preferences package provides a simple API for managing application
preferences. The classes in the package are implemented using a layered
approach where the lowest layer provides access to the raw preferences
mechanism and each layer on top providing more convenient ways to get and set
preference values.

The Basic Preferences Mechanism
-------------------------------

Lets start by taking a look at the lowest layer which consists of the
|IPreferences| interface and its default implementation in the |Preferences|
class. This layer implements the basic preferences system which is a
hierarchical arrangement of preferences 'nodes' (where each node is simply an
object that implements the |IPreferences| interface). Nodes in the hierarchy can
contain preference settings and/or child nodes. This layer also provides a
default way to read and write preferences from the filesystem using the
excellent `ConfigObj`_ package.

This all sounds a bit complicated but, believe me, it isn't! To prove it
(hopefully) lets look at an example. Say I have the following preferences in
a file 'example.ini'::

  [acme.ui]
  bgcolor = blue
  width = 50
  ratio = 1.0
  visible = True

  [acme.ui.splash_screen]
  image = splash
  fgcolor = red

I can create a preferences hierarchy from this file by::

  >>> from apptools.preferences.api import Preferences
  >>> preferences = Preferences(filename='example.ini')
  >>> preferences.dump()

   Node() {}
     Node(acme) {}
       Node(ui) {'bgcolor': 'blue', 'width': '50', 'ratio': '1.0', 'visible': 'True'}
         Node(splash_screen) {'image': 'splash', 'fgcolor': 'red'}

The 'dump' method (useful for debugging etc) simply 'pretty prints' a
preferences hierarchy. The dictionary next to each node contains the node's
actual preferences. In this case, the root node (the node with no name) is the
preferences object that we created. This node now has one child node 'acme',
which contains no preferences. The 'acme' node has one child, 'ui', which
contains some preferences (e.g. 'bgcolor') and also a child node
'splash_screen' which also contains preferences (e.g. 'image').

To look up a preference we use::

  >>> preferences.get('acme.ui.bgcolor')
  'blue'

If no such preferences exists then, by default, None is returned::

  >>> preferences.get('acme.ui.bogus') is None
  True

You can also specify an explicit default value::

  >>> preferences.get('acme.ui.bogus', 'fred')
  'fred'

To set a preference we use::

  >>> preferences.set('acme.ui.bgcolor', 'red')
  >>> preferences.get('acme.ui.bgcolor')
  'red'

And to make sure the preferences are saved back to disk::

  >>> preferences.flush()

To add a new preference value we simply set it::

  >>> preferences.set('acme.ui.fgcolor', 'black')
  >>> preferences.get('acme.ui.fgcolor')
  'black'

Any missing nodes in a call to 'set' are created automatically, hence::

  >>> preferences.set('acme.ui.button.fgcolor', 'white')
  >>> preferences.get('acme.ui.button.fgcolor')
  'white'

Preferences can also be 'inherited'. e.g. Notice that the 'splash_screen'
node does not contain a 'bgcolor' preference, and hence::

   >>> preferences.get('acme.ui.splash_screen.bgcolor') is None
   True

But if we allow the 'inheritance' of preference values then::

   >>> preferences.get('acme.ui.splash_screen.bgcolor', inherit=True)
   'red'

By using 'inheritance' here the preferences system will try the following
preferences::

  'acme.ui.splash_screen.bgcolor'
  'acme.ui.bgcolor'
  'acme.bgcolor'
  'bgcolor'

Strings, Glorious Strings
~~~~~~~~~~~~~~~~~~~~~~~~~

At this point it is worth mentioning that preferences are *always* stored and
returned as strings. This is because of the limitations of the traditional
'.ini' file format i.e. they don't contain any type information! Now before you
start panicking, this doesn't mean that all of your preferences have to be
strings! Currently the preferences system allows, strings(!), booleans, ints,
longs, floats and complex numbers. When you store a non-string value it gets
converted to a string for you, but you *always* get a string back::

  >>> preferences.get('acme.ui.width')
  '50'
  >>> preferences.set('acme.ui.width', 100)
  >>> preferences.get('acme.ui.width')
  '100'

  >>> preferences.get('acme.ui.visible')
  'True'
  >>> preferences.set('acme.ui.visible', False)
  >>> preferences.get('acme.ui.visible')
  'False'

This is obviously not terribly convenient, and so the following section
discusses how we associate type information with our preferences to make
getting and setting them more natural.

Preferences and Types
---------------------

As mentioned previously, we would like to be able to get and set non-string
preferences in a more convenient way. This is where the |PreferencesHelper|
class comes in.

Let's take another look at 'example.ini'::

  [acme.ui]
  bgcolor = blue
  width = 50
  ratio = 1.0
  visible = True

  [acme.ui.splash_screen]
  image = splash
  fgcolor = red

Say, I am interested in the preferences in the 'acme.ui' section. I can use a
preferences helper as follows::

  from apptools.preferences.api import PreferencesHelper

  class SplashScreenPreferences(PreferencesHelper):
      """ A preferences helper for the splash screen. """

      preferences_path = 'acme.ui'

      bgcolor = Str
      width   = Int
      ratio   = Float
      visible = Bool

  >>> preferences = Preferences(filename='example.ini')
  >>> helper = SplashScreenPreferences(preferences=preferences)
  >>> helper.bgcolor
  'blue'
  >>> helper.width
  50
  >>> helper.ratio
  1.0
  >>> helper.visible
  True

And, obviously, I can set the value of the preferences via the helper too::

  >>> helper.ratio = 0.5

And if you want to prove to yourself it really did set the preference::

  >>> preferences.get('acme.ui.ratio')
  '0.5'

Using a preferences helper you also get notified via the usual trait
mechanism when the preferences are changed (either via the helper or via the
preferences node directly::

  def listener(obj, trait_name, old, new):
      print(trait_name, old, new)

  >>> helper.on_trait_change(listener)
  >>> helper.ratio = 0.75
  ratio 0.5 0.75
  >>> preferences.set('acme.ui.ratio', 0.33)
  ratio 0.75 0.33

Scoped Preferences
------------------

In many applications the idea of preferences scopes is useful. In a scoped
system, an actual preference value can be stored in any scope and when a call
is made to the 'get' method the scopes are searched in order of precedence.

The default implementation (in the |ScopedPreferences| class) provides two
scopes by default:

1) The application scope

This scope stores itself in the 'ETSConfig.application_home' directory. This
scope is generally used when *setting* any user preferences.

2) The default scope

This scope is transient (i.e. it does not store itself anywhere). This scope
is generally used to load any predefined default values into the preferences
system.

If you are happy with the default arrangement, then using the scoped
preferences is just like using the plain old non-scoped version::

  >>> from apptools.preferences.api import ScopedPreferences
  >>> preferences = ScopedPreferences(filename='example.ini')
  >>> preferences.load('example.ini')
  >>> preferences.dump()

   Node() {}
     Node(application) {}
       Node(acme) {}
         Node(ui) {'bgcolor': 'blue', 'width': '50', 'ratio': '1.0', 'visible': 'True'}
           Node(splash_screen) {'image': 'splash', 'fgcolor': 'red'}
     Node(default) {}

Here you can see that the root node now has a child node representing each
scope.

When we are getting and setting preferences using scopes we generally want the
following behaviour:

a) When we get a preference we want to look it up in each scope in order. The
first scope that contains a value 'wins'.

b) When we set a preference, we want to set it in the first scope. By default
this means that when we set a preference it will be set in the application
scope. This is exactly what we want as the application scope is the scope that
is persistent.

So usually, we just use the scoped preferences as before::

  >>> preferences.get('acme.ui.bgcolor')
  'blue'
  >>> preferences.set('acme.ui.bgcolor', 'red')
  >>> preferences.dump()

   Node() {}
     Node(application) {}
       Node(acme) {}
         Node(ui) {'bgcolor': 'red', 'width': '50', 'ratio': '1.0', 'visible': 'True'}
           Node(splash_screen) {'image': 'splash', 'fgcolor': 'red'}
     Node(default) {}

And, conveniently, preference helpers work just the same with scoped
preferences too::

  >>> helper = SplashScreenPreferences(preferences=preferences)
  >>> helper.bgcolor
  'red'
  >>> helper.width
  50
  >>> helper.ratio
  1.0
  >>> helper.visible
  True

Accessing a particular scope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Should you care about getting or setting a preference in a particular scope
then you use the following syntax::

  >>> preferences.set('default/acme.ui.bgcolor', 'red')
  >>> preferences.get('default/acme.ui.bgcolor')
  'red'
  >>> preferences.dump()

   Node() {}
     Node(application) {}
       Node(acme) {}
         Node(ui) {'bgcolor': 'red', 'width': '50', 'ratio': '1.0', 'visible': 'True'}
           Node(splash_screen) {'image': 'splash', 'fgcolor': 'red'}
     Node(default) {}
       Node(acme) {}
         Node(ui) {'bgcolor': 'red'}

You can also get hold of a scope via::

  >>> default = preferences.get_scope('default')

And then perform any of the usual operations on it.

Further Reading
---------------

So that's a quick tour around the basic useage of the preferences API. For more
information about what is provided take a look at the :ref:`api-documentation`.

If you are using Envisage to build your applications then you might also be
interested in the |Preferences in Envisage| section.

..
   external links

.. _ConfigObj: https://configobj.readthedocs.io/en/latest

..
   # substitutions

.. |ScopedPreferences| replace:: :class:`~apptools.preferences.scoped_preferences.ScopedPreferences`
.. |IPreferences| replace:: :class:`~apptools.preferences.i_preferences.IPreferences`
.. |Preferences| replace:: :class:`~apptools.preferences.preferences.Preferences`
.. |PreferencesHelper| replace:: :class:`~apptools.preferences.preferences_helper.PreferencesHelper`
.. |Preferences in Envisage| replace:: :ref:`preferences-in-envisage`
