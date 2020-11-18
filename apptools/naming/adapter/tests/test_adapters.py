

import unittest

from traits.api import HasTraits, TraitDict, TraitList
from traits.adaptation.api import (
    adapt,
    AdaptationManager,
    get_global_adaptation_manager,
    register_factory,
    set_global_adaptation_manager
)

from apptools.naming import Context
from apptools.naming.adapter import *

class TestAdapters(unittest.TestCase):

    def setUp(self):
        # Set new/empty global adaptation manager and store the old one.
        self.old_adaptation_manager = get_global_adaptation_manager()
        self.adaptation_manager = AdaptationManager()
        set_global_adaptation_manager(self.adaptation_manager)

    def tearDown(self):
        # Restore state of global adaptation manager.
        set_global_adaptation_manager(self.old_adaptation_manager)

    def test_dict_context_adapter(self):
        register_factory(DictContextAdapter, dict, Context)
        some_dict = {'a': 1, 'b': 2}
        self.assertIsNotNone(adapt(some_dict, Context, default=None))

    def test_list_context_adapter(self):
        register_factory(ListContextAdapter, list, Context)
        some_list = ['a', 'b']
        self.assertIsNotNone(adapt(some_list, Context, default=None))

    def test_instance_context_adapter(self):
        register_factory(InstanceContextAdapter, object, Context)
        class A:
            pass
        self.assertIsNotNone(adapt(A(), Context, default=None))

    def test_trait_dict_context_adapter(self):
        register_factory(TraitDictContextAdapter, TraitDict, Context)
        print(type(A().some_dict))
        class A(HasTraits):
            some_dict = {'a': 1}
        self.assertIsNotNone(adapt(A().some_dict, Context, default=None))

    def test_trait_list_context_adapter(self):
        register_factory(TraitListContextAdapter, TraitDict, Context)
        class A(HasTraits):
            some_dict = {'a': 1}
        print(type(A().some_dict))
        self.assertIsNotNone(adapt(A().some_dict, Context, default=None))