.. _selection_service:

The selection service
=====================

It is quite common in GUI applications to have a UI element displaying a
collection of items that a user can select ("selection providers"), while
other parts of the application must react to changes in the selection
("selection listeners").

Ideally, the listeners would not have a direct dependency on the UI object.
This is especially important in extensible `envisage`_ applications, where
a plugin might need to react to a selection change, but we do not want to
expose the internal organization of the application to external developers.

This package defines a selection service that manages the communication
between providers and listener.


The :class:`~.SelectionService` object
--------------------------------------

The :class:`~.SelectionService` object is the central manager that handles
the communication between selection providers and listener.

:ref:`Selection providers <selection_providers>` are components that wish to
publish information about their current selection for public consumption.
They register to a selection
service instance when they first have a selection available (e.g., when the
UI showing a list of selectable items is initialized), and un-register as soon
as the selection is not available anymore (e.g., the UI is destroyed when the
windows is closed).

:ref:`Selection listeners <selection_listeners>` can query the selection
service to get the current selection published by a provider, using the
provider unique ID.

The service acts as a broker between providers and listeners, making sure that
they are notified when the
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.selection`
event is fired.

.. _selection_providers:

Selection providers
-------------------

Any object can become a selection provider by implementing the
:class:`~apptools.selection.i_selection_provider.ISelectionProvider`
interface, and registering to the selection service.

Selection providers must provide a unique ID
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.provider_id`,
which is used by listeners to request its current selection.

Whenever its selection changes, providers fire a
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.selection`
event. The content of the event is an instance implementing
:class:`~.ISelection` that contains information about the selected items.
For example, a :class:`~.ListSelection` object contains a list of selected
items, and their indices.

Selection providers can also be queried directly about their current selection
using the
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.get_selection`
method, and can be requested to change their selection to a new one with the
:attr:`~apptools.selection.i_selection_provider.ISelectionProvider.set_selection`
method.

Registration
~~~~~~~~~~~~

Selection providers publish their selection by registering to the selection
service using the
:attr:`~apptools.selection.selection_service.SelectionService.add_selection_provider`
method. When the selection is no longer available, selection providers
should un-register through
:attr:`~apptools.selection.selection_service.SelectionService.remove_selection_provider`.

Typically, selection providers are UI objects showing a list or tree of items,
they register as soon as the UI component is initialized, and un-register
when the UI component disappears (e.g., because their window has been closed).
In more complex applications, the registration could be done by a controller
object instead.

.. _selection_listeners:

Selection listeners
-------------------

Selection listeners request information regarding the current selection
of a selection provider given their provider ID. The :class:`~.SelectionService`
supports two distinct use cases:

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

It is possible for a listener to connect to a provider ID before it is
registered. As soon as the provider is registered, the listener will receive
a notification containing the provider's initial selection.

To disconnect a listener use the methods
:attr:`~apptools.selection.selection_service.SelectionService.disconnect_selection_listener`.

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
a :class:`~apptools.selection.errors.ProviderNotRegisteredError` is raised,
unless the optional keyword argument :attr:`ignore_missing` is set to ``True``.

.. _envisage: http://docs.enthought.com/envisage/
