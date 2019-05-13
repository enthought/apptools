""" Tests the type manager. """


# Standard library imports.
import unittest

# Enthought library imports.
from traits.api import HasTraits, Instance, Str
from apptools.type_manager import AdapterFactory, Factory, TypeManager


# Test classes.
class Foo(HasTraits):
    name = Str

    def foogle(self):
        return 'Foo.foogle.%s' % self.name


class SubOfFoo(Foo):
    def foogle(self):
        return 'Sub.foogle.%s' % self.name

class EmptySubOfFoo(Foo):
    pass

class Bar(HasTraits):
    name = Str
    def blargle(self):
        return 'Bar.blargle.%s' % self.name


# Test adapters and factories.
class FooToBarAdapter(HasTraits):
    adaptee = Instance(Foo)

    def blargle(self):
        return self.adaptee.foogle()

class FooToBarAdapterFactory(AdapterFactory):

    #### 'AdapterFactory' interface ###########################################

    # The type of object that the factory can adapt.
    adaptee_class = Foo

    # The adapter class (the class that adapts the adaptee to the target
    # class).
    adapter_class = FooToBarAdapter

    # The target class (the class that the factory can adapt objects to).
    target_class = Bar


class SubOfFooToBarAdapter(HasTraits):
    adaptee = Instance(SubOfFoo)

    def blargle(self):
        return self.adaptee.foogle()

class SubOfFooToBarAdapterFactory(AdapterFactory):
    #### 'AdapterFactory' interface ###########################################

    # The type of object that the factory can adapt.
    adaptee_class = SubOfFoo

    # The adapter class (the class that adapts the adaptee to the target
    # class).
    adapter_class = SubOfFooToBarAdapter

    # The target class (the class that the factory can adapt objects to).
    target_class = Bar


class BarFactory(Factory):
    def can_create(self, target_class, *args, **kw):
        return target_class is Bar

    def create(self, target_class, *args, **kw):
        return Bar(*args, **kw)


class TypeManagerTestCase(unittest.TestCase):
    """ Tests the type manager. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        # An empty type manager.
        self.type_manager = TypeManager()

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_no_adapter_required(self):
        """ no adapter required """

        # Create a Bar.
        b = Bar()

        # Try to adapt it to a Bar.
        bar = self.type_manager.object_as(b, Bar)

        # The type manager should simply return the same object.
        self.assert_(bar is b)

        return

    def test_no_adapter(self):
        """ no adapter available """

        # Create a Foo.
        foo = Foo(name='fred')

        # Try to adapt it to a bar.
        bar = self.type_manager.object_as(foo, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_instance_adapter(self):
        """ instance adapter """

        # Create a Foo.
        foo = Foo(name='fred')

        # Register an adapter Foo->Bar on the INSTANCE (this one should take
        # precedence).
        self.type_manager.register_instance_adapters(
            FooToBarAdapterFactory(), foo
        )

        # Register an adapter Foo->Bar on the TYPE (this will fail if it gets
        # picked up since it won't actually adapt 'Foo' objects!).
        self.type_manager.register_instance_adapters(
            SubOfFooToBarAdapterFactory(), Foo
        )

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Foo.foogle.fred')

        return

    def test_unregister_instance_adapter(self):
        """ unregister instance adapter """

        # Create a Foo.
        foo = Foo(name='fred')

        # The factory.
        factory = FooToBarAdapterFactory()

        # Register an adapter Foo->Bar on the INSTANCE (this one should take
        # precedence).
        self.type_manager.register_instance_adapters(factory, foo)

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Foo.foogle.fred')

        # Remove the adapter.
        self.type_manager.unregister_instance_adapters(factory, foo)

        # Now we shouldn't be able to adapt the object.
        #
        # Try to adapt it to a bar.
        bar = self.type_manager.object_as(foo, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_adapter_on_class(self):
        """ an adapter registered on an object's actual class. """

        # Register an adapter Foo->Bar.
        self.type_manager.register_type_adapters(FooToBarAdapterFactory(), Foo)

        # Create a Foo.
        foo = Foo(name='fred')

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Foo.foogle.fred')

        return

    def test_adapter_on_base_class(self):
        """ an adapter registered on one of an object's base classes. """

        # Register an adapter Foo->Bar.
        self.type_manager.register_type_adapters(FooToBarAdapterFactory(), Foo)

        # Create an instance of a class derived from Foo.
        sub = SubOfFoo(name='fred')

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(sub, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Sub.foogle.fred')

        return

    def test_ignore_adapter_on_class(self):
        """ ignore an adapter on an object's actual class. """

        # Register an adapter SubOfFoo->Bar on the Foo class.
        self.type_manager.register_type_adapters(
            SubOfFooToBarAdapterFactory(), Foo
        )

        # Create a Foo.
        foo = Foo(name='fred')

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_ignore_adapter_on_derived_class(self):
        """ ignore an adapter registered on a derived class. """

        # Register an adapter Foo->Bar on the SubOfFoo class.
        self.type_manager.register_type_adapters(
            FooToBarAdapterFactory(), SubOfFoo
        )

        # Create a Foo.
        foo = Foo(name='fred')

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_unregister_adapter(self):
        """ unregister an adapter. """

        factory = FooToBarAdapterFactory()

        # Register an adapter Foo->Bar.
        self.type_manager.register_type_adapters(factory, Foo)

        # Create a Foo.
        foo = Foo(name='fred')

        # Adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Foo.foogle.fred')

        # Unregister the adapter.
        self.type_manager.unregister_type_adapters(factory)

        # Try to adapt it to a Bar.
        bar = self.type_manager.object_as(foo, Bar)

        # There should be no way to adapt a Foo to a Bar.
        self.assertEqual(bar, None)

        return

    def test_factory(self):
        """ simple factory """

        # Create a Bar factory.
        factory = BarFactory()

        # Try to create a Bar using the factory.
        bar = self.type_manager.object_as(factory, Bar, name='joe')
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Bar.blargle.joe')

        return

    def test_pre_hook(self):
        """ pre hook """

        l = []
        def hook(*args, **kw):
            l.append('Hello')

        # Create a Foo.
        foo = Foo(name='fred')

        # Hook a method.
        self.type_manager.add_pre(Foo, 'foogle', hook)

        # Call the method that we have hooked.
        foo.foogle()

        # Make sure that the hook was called.
        self.assertEqual(len(l), 1)

        # Remove the hook.
        self.type_manager.remove_pre(Foo, 'foogle', hook)

        # Call the method that we have hooked.
        foo.foogle()

        # Make sure that the hook was NOT called.
        self.assertEqual(len(l), 1)

        return

    def test_post_hook(self):
        """ post hook """

        def hook(result, *args, **kw):
            return 'Hello'

        # Create a Foo.
        foo = Foo(name='fred')

        # Hook a method.
        self.type_manager.add_post(Foo, 'foogle', hook)

        # Call the method that we have hooked.
        self.assertEqual(foo.foogle(), 'Hello')

        # Remove the hook.
        self.type_manager.remove_post(Foo, 'foogle', hook)

        # Call the method that we have hooked.
        foo.foogle()

        # Make sure that the hook was NOT called.
        self.assertEqual(foo.foogle(), 'Foo.foogle.fred')

        return

    def test_pre_hook_on_inherited_method(self):
        """ test pre hook on an inherited method """

        l = []
        def hook(*args, **kw):
            l.append('Hello')

        # Create an instance of a subclass of Foo that does NOT override
        # 'foogle'.
        esof = EmptySubOfFoo(name='fred')

        # Prove that it does not override 'foogle'!
        method = EmptySubOfFoo.__dict__.get('foogle')
        self.assertEqual(method, None)

        # Hook a method.
        self.type_manager.add_pre(EmptySubOfFoo, 'foogle', hook)

        # Make sure that the method was added to the class dictionary.
        method = EmptySubOfFoo.__dict__.get('foogle')
        self.assertNotEqual(method, None)

        # Call the method that we have hooked.
        esof.foogle()

        # Make sure that the hook was called.
        self.assertEqual(len(l), 1)

        # Remove the hook.
        self.type_manager.remove_pre(EmptySubOfFoo, 'foogle', hook)

        # Call the method that we have hooked.
        esof.foogle()

        # Make sure that the hook was NOT called.
        self.assertEqual(len(l), 1)

        # Make sure that we didn't put the original method back onto
        # 'EmptySubOfFoo'(since it didn't override it in the first place).
        method = EmptySubOfFoo.__dict__.get('foogle')
        self.assertEqual(method, None)

        return

    def test_type_manager_hierarchy(self):
        """ type manager hierarchy """

        # Register an adapter Foo->Bar.
        self.type_manager.register_type_adapters(FooToBarAdapterFactory(), Foo)

        # Create an empy type manager with the main type manager as its
        # parent.
        type_manager = TypeManager(parent=self.type_manager)

        # Create a Foo.
        foo = Foo(name='fred')

        # Adapt it to a Bar.
        bar = type_manager.object_as(foo, Bar)
        self.assertNotEqual(bar, None)
        self.assertEqual(bar.blargle(), 'Foo.foogle.fred')

        return

#### EOF ######################################################################
