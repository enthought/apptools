from traits import trait_notifiers
from traits.api import (
    Bool, Button, cached_property, Float, HasStrictTraits, Instance, List,
    Property, Unicode)
from traits.util.event_tracer import (
    CallingMessageRecord, ChangeMessageRecord, ExitMessageRecord,
    MultiThreadChangeEventRecorder, MultiThreadRecordContainer, SentinelRecord)
from traitsui.api import (
    ButtonEditor, Item, HGroup, TreeEditor, TreeNode, UItem, VGroup, View)
from pyface.timer.api import Timer


CHANGE_TEMPLATE = (
    u"{class_name}.{name}: {old!r} \N{RIGHTWARDS ARROW} {new!r}")
CALLING_TEMPLATE = u"{handler} ({source})"


def change_records_equal(record1, record2):
    """ Return True if the two records are equal. """
    cond = (record1.name == record2.name
            and record1.old is record2.old
            and record1.new is record2.new
            and record1.class_name == record2.class_name)
    return cond


def records_to_tree(records, idx):
    """ Transform a list of record in a tree (list-of-lists) recursively.
    """

    sub_events = []
    # Top-level change event for the sub-tree.
    change_msg_record = records[idx]
    assert isinstance(change_msg_record, ChangeMessageRecord)
    # Sub-tree indentation.
    current_indent = change_msg_record.indent

    idx += 1
    n_records = len(records)
    while idx < n_records:
        next_record = records[idx]
        if isinstance(next_record, SentinelRecord):
            idx += 1
        elif isinstance(next_record, ExitMessageRecord):
            idx += 1
        elif isinstance(next_record, CallingMessageRecord):
            called_record = CalledRecord(next_record)
            sub_events.append(called_record)
            idx += 1
        elif isinstance(next_record, ChangeMessageRecord):
            # if larger indent, new event
            if next_record.indent > current_indent:
                event, idx = records_to_tree(records, idx)
                sub_events.append(event)
            else:
                # if same indent and equality -> continue
                if (change_records_equal(next_record, change_msg_record)
                        and next_record.indent == current_indent):
                    idx += 1
                # if same indent but no equality, or smaller indent -> exit
                # (new event at same level)
                else:
                    break

    event = Event(change_msg_record, sub_events)

    return event, idx


class CalledRecord(HasStrictTraits):
    """ Tree representation of an event for a called notification method. """
    txt = Unicode
    time = Unicode

    def __init__(self, calling_msg_record):
        super(CalledRecord, self).__init__()
        self.txt = CALLING_TEMPLATE.format(
            handler=calling_msg_record.handler,
            source=calling_msg_record.source
        )
        self.time = unicode(calling_msg_record.time)


class Event(HasStrictTraits):
    """ Tree representation of a change event. """
    txt = Unicode
    time = Unicode
    sub_events = List

    def __init__(self, change_msg_record, sub_events):
        super(Event, self).__init__()
        self.txt = CHANGE_TEMPLATE.format(
            name=change_msg_record.name,
            old=change_msg_record.old,
            new=change_msg_record.new,
            class_name=change_msg_record.class_name,
        )
        self.time = unicode(change_msg_record.time)
        self.sub_events = sub_events


class Thread(HasStrictTraits):
    """ Tree representation of a list of events for one thread. """
    events = List(Event)
    txt = Unicode
    time = Unicode

    def __init__(self, thread_name, record_container):
        super(Thread, self).__init__()
        events = []
        records = record_container._records
        idx = 0
        n_records = len(records)
        while idx < n_records:
            if not isinstance(records[idx], ChangeMessageRecord):
                idx += 1
                continue
            change_evt = records[idx]
            event, idx = records_to_tree(records, idx)
            if change_evt.class_name != 'NotViewer':
                events.append(event)
        self.events = events
        self.txt = 'Thread {}'.format(thread_name)


class ThreadList(HasStrictTraits):
    """ Tree representation of a list of threads. """
    threads = List(Thread)

    def __init__(self, record_containers):
        super(ThreadList, self).__init__()
        threads = []
        for thread_name, record_container in record_containers.items():
            thread = Thread(
                thread_name=thread_name,
                record_container=record_container
            )
            threads.append(thread)
        self.threads = threads


tree_editor = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[ThreadList],
            auto_open=True,
            children='threads',
            label='=Traits notification events',
        ),
        TreeNode(
            node_for=[Thread],
            auto_open=True,
            children='events',
            label='txt',
        ),
        TreeNode(
            node_for=[Event],
            auto_open=False,
            children='sub_events',
            label='txt',
            tooltip='time',
            icon_group='change.png',
            icon_open='change.png',
        ),
        TreeNode(
            node_for=[CalledRecord],
            label='txt',
            tooltip='time',
            icon_item='calling.png',
        ),
    ],
    hide_root=True,
    editable=False,
)


class NotViewer(HasStrictTraits):

    #: Time between updated, in msec.
    update_time = Float(100)

    #: Traits notification events recorder.
    _recorder = Instance(MultiThreadChangeEventRecorder)

    #: Traits notification events container.
    _container = Instance(MultiThreadRecordContainer)

    #: List of thread representations. These are the top branches of the tree.
    _thread_list = Instance(ThreadList)

    #: Timer to update spinning.
    _spin_timer = Instance(Timer)

    #: Button to start/stop recording.
    _record_button = Button()

    #: Label on top of the record button.
    _record_label = Property(Unicode, depends_on='_recording')

    #: Message displaying recording status.
    _recording = Bool(False)

    def start(self):
        self._recording = True
        self._container = MultiThreadRecordContainer()
        self._recorder = MultiThreadChangeEventRecorder(self._container)

        trait_notifiers.set_change_event_tracers(
            pre_tracer=self._recorder.pre_tracer,
            post_tracer=self._recorder.post_tracer
        )

        self._spin_timer = Timer(self.update_time, self.update_view)

    def stop(self):
        if self._recorder is not None:
            self._spin_timer.Stop()
            self._spin_timer = None

            self._recording = False
            trait_notifiers.clear_change_event_tracers()
            self._recorder.close()
            self.update_view()

            self._recorder = None

    def update_view(self):
        self._thread_list = ThreadList(self._container._record_containers)

    def default_traits_view(self):
        view = View(
            VGroup(
                HGroup(
                    UItem(
                        '_record_button',
                        editor=ButtonEditor(label_value='_record_label')
                    ),
                    Item(
                        'update_time',
                        label='Update interval (ms)',
                        enabled_when='not _recording',
                    ),
                ),
                VGroup(
                    UItem(
                        '_thread_list',
                        editor=tree_editor,
                        enabled_when='not _recording',
                    ),
                    show_border=True,
                ),
            ),
            title='NotViewer',
            height=800,
            width=500,
            resizable=True,
        )
        return view

    def __thread_list_default(self):
        return ThreadList({})

    @cached_property
    def _get__record_label(self):
        if self._recording:
            return 'Stop recording'
        else:
            return 'Start recording'

    def __record_button_fired(self):
        if self._recording:
            self.stop()
        else:
            self.start()
