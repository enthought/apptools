from setuptools import setup, find_packages

setup(
    name = 'enthought.help',
    version = '3.0a1',
    description  = 'Help framework for envisage applications',
    author       = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    url          = 'http://code.enthought.com/ets',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "enthought.logger",
        "enthought.traits",
    ],
    extras_require = {
        "EnvisagePlugin": ["enthought.envisage"],
    },
    namespace_packages = [
        "enthought",
    ],
)

