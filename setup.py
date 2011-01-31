from setuptools import setup
        
# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")
        
setup(
#    install_requires = ['cothread'], # require statements go here
    name = 'dls_pmaccontrol',
    version = version,
    description = 'Module',
    author = 'fgz73762',
    author_email = 'fgz73762@rl.ac.uk',    
    packages = ['dls_pmaccontrol'],
#    entry_points = {'console_scripts': ['test-python-hello-world = dls_pmaccontrol.dls_pmaccontrol:main']}, # this makes a script
#    include_package_data = True, # use this to include non python files
    zip_safe = False
    )        
