"""A simple example of an object model."""


# Enthought library imports.
from enthought.permissions.api import SecureHandler
from enthought.traits.api import HasTraits, Int, Unicode
from enthought.traits.ui.api import Item, View

# Local imports.
from permissions import UpdatePersonAgePerm, PersonSalaryPerm


class Person(HasTraits):
    """A simple example of an object model"""

    # Name.
    name = Unicode

    # Age in years.
    age = Int

    # Salary.
    salary = Int

    # Define the default view with permissions attached.
    age_perm = UpdatePersonAgePerm
    salary_perm = PersonSalaryPerm

    traits_view = View(
            Item(name='name'),
            Item(name='age', enabled_when='object.age_perm.granted'),
            Item(name='salary', visible_when='object.salary_perm.granted'),
            handler=SecureHandler)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __str__(self):
        """Return an informal string representation of the object."""

        return self.name

#### EOF ######################################################################
