""" A simple example of the NotViewer in action.

This script opens a simple Traits UI view together with the Traits
notification viewer window. Start the recording and play with the traits to
see what happens behind the scenes.
"""

from traits.api import HasStrictTraits, Instance, Int, Range, on_trait_change
from traitsui.api import Item, View
from apptools.traits_utils.notviewer import NotViewer


class Foo(HasStrictTraits):

    a = Int

    b = Int

    def _a_changed(self):
        pass

    def _b_changed(self):
        pass


class Bar(HasStrictTraits):

    foo = Instance(Foo)

    twice_a = Int

    moo = Range(1, 100)

    @on_trait_change('foo.a')
    def _react_to_foo_a(self):
        self.twice_a = self.foo.a * 2
        self.foo.b = self.foo.a + 1
        self.foo.b = self.foo.a + 2

    def default_traits_view(self):
        view = View(
            Item('object.foo.a'),
            Item('twice_a'),
            Item('moo'),
        )
        return view


if __name__ == '__main__':
    foo = Foo(a=32)
    bar = Bar(foo=foo)

    notviewer = NotViewer()
    ui = notviewer.edit_traits()

    bar.configure_traits()
