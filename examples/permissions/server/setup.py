# Major package imports.
from setuptools import setup, find_packages

setup(
    name                 = 'PermissionsServer',
    version              = '1.0',
    author               = 'Riverbank Computing Limited',
    author_email         = 'info@riverbankcomputing.com',
    license              = 'BSD',
    zip_safe             = True,
    packages             = find_packages(),
    include_package_data = True,

    namespace_packages   = [
        'enthought'
    ],
)
