.. _selection_service:

The selection service
=====================

It is quite common in GUI applications to have a UI element displaying a
collection of items that a user can select ("selection providers"), while
other parts of the application must react to changes in the selection
("selection listeners").

Ideally, the listeners would not have a direct dependency on the UI object.
This is especially important in extensible ``envisage`` application, where
a plugin might need to react to a selection change, but we do not want to
expose the internal organization of the application to external developers.

This package defines a selection service that manages the communication
between providers and listener.


The :class:`~.SelectionService` object
--------------------------------------

The :class:`~SelectionService` object is the central manager that handles
the communication between selection providers and listener.

It supports two distinct use cases:

 1) Passively listening to selection changes: listener connect to a specific
    provider and are notified when the provider's selection changes.

 2) Actively querying a provider for its current selection: the selection
    service can be used to query a provider using its unique ID.

Passive listening
~~~~~~~~~~~~~~~~~

Listeners connect to the selection events for a given provider using the
:attr:`~apptools.selection.selection_service.SelectionService.connect_selection_listener`
method. They need to provide the unique ID of the provider, and a function
(or callable) that is called to send the event. This callback function takes
one argument, an implementation of the :class:`~.ISelection` that represents
the selection.

On their side, providers need to register to the selection service through
:attr:`~apptools.selection.selection_service.SelectionService.add_selection_provider`.
When their selection changes, providers emit a
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.selection`
event that contains an :class:`~.ISelection` instance.

The service acts as a broker between providers and listeners, making sure that
they are notified when the
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.selection`
event is fired.

It is possible for a listener to connect to a provider ID before it is
registered. As soon as the provider is registered, the listener will receive
a notification containing the provider's initial selection.

To disconnect a listener / unregister a provider use the methods
:attr:`~apptools.selection.selection_service.SelectionService.disconnect_selection_listener`
and
:attr:`~apptools.selection.selection_service.SelectionService.remove_selection_provider`

Active querying
~~~~~~~~~~~~~~~

In other instances, an element of the application only needs the current
selection at a specific time. For example, a toolbar button could open dialog
representing a user action based on what is currently selected in the active
editor.

The
:attr:`~apptools.selection.selection_service.SelectionService.get_selection`
method calls the corresponding method on the provider with the given ID and
returns an :class:`~.ISelection` instance.

Setting a selection
~~~~~~~~~~~~~~~~~~~

Finally, it is possible to request a provider to set its selection to a given
set of objects with
:attr:`~apptools.selection.selection_service.SelectionService.set_selection`.
The main use case for this method is multiple views of the same list of
objects, which need to keep their selection synchronized.

If the items specified in the arguments are not available in the provider,
a :class:`~.ProviderNotRegisteredError` is raised, unless the optional
keyword argument :attr:`ignore_missing` is set to ``True``.


API Reference
-------------

:mod:`apptools.selection` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users of the :mod:`apptools.selection` package can access the objects that are
part of the public API through the convenience :mod:`apptools.selection.api`.

:mod:`~apptools.selection.selection_service` Module
''''''''''''''''''''''''''''''''''''''''''''''''''

.. automodule:: apptools.selection.selection_service
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~apptools.selection.i_selection_provider` Module
'''''''''''''''''''''''''''''''''''''''''''''''''''''

.. automodule:: apptools.selection.i_selection_provider
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~apptools.selection.is_selection` Module
'''''''''''''''''''''''''''''''''''''''''''''

.. automodule:: apptools.selection.i_selection
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~apptools.selection.list_selection` Module
'''''''''''''''''''''''''''''''''''''''''''''''

.. automodule:: apptools.selection.list_selection
    :members:
    :undoc-members:
    :show-inheritance:
