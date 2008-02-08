"""The definitions of all the permissions used in the example."""


from enthought.permissions.api import Permission


# Access to the Debug view.
DebugViewPerm = Permission(id='ets.permissions.example.debug.view',
        description=u"Use the debug view")

# Add a new person.
NewPersonPerm = Permission(id='ets.permissions.example.person.new',
        description=u"Add a new person")

# Update a person's age.
UpdatePersonAgePerm = Permission(id='ets.permissions.example.person.age.update',
        description=u"Update a person's age")

# View or update a person's salary.
PersonSalaryPerm = Permission(id='ets.permissions.example.person.salary',
        description=u"View or update a person's salary")

# Enable the example toolkit specific widget.
EnableWidgetPerm = Permission(id='ets.permissions.example.widget',
        description=u"Enable the example toolkit specific widget")
