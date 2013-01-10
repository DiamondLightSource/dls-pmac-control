# DLS environment settings
PREFIX = $(PWD)/prefix
PYTHON = dls-python
PYUIC=pyuic4

## Mac OS X settings.
#PYTHON = python2.6
#INSTALL_DIR = /Users/ulrik/python/install/packages
#SCRIPT_DIR = /Users/ulrik/python/install/scripts
#PYUIC=pyuic4-2.6

## Ubuntu settings
#PYTHON = python
#INSTALL_DIR = /home/ulrik/python/install/packages
#SCRIPT_DIR = /home/ulrik/python/install/scripts
#PYUIC=pyuic4


MODULEVER = 1.6

# Override with any release info
-include Makefile.private

# uic files
UICS=$(patsubst %.ui, %.py, $(wildcard dls_pmaccontrol/*.ui))

# build the screens from .ui source
%.py: %.ui
	$(PYUIC) -o $@ $<

# This is run when we type make
# It can depend on other targets e.g. the .py files produced by pyuic4 
dist: setup.py $(wildcard dls_pmaccontrol/*.py) $(UICS)
	MODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
	touch dist
	$(MAKE) -C documentation 

# Clean the module
clean:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info installed.files $(UICS)
	-find -name '*.pyc' -exec rm {} \;
	$(MAKE) -C documentation clean

# Install the built egg and keep track of what was installed
install: dist
	$(PYTHON) setup.py easy_install -m \
		--record=installed.files \
		--prefix=$(PREFIX) dist/*.egg        
