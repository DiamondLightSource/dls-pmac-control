# Specify defaults for testing
PREFIX = /scratch/tools
#PREFIX = /dls_sw/prod/tools/RHEL5
PYTHON = $(PREFIX)/bin/python2.6
INSTALL_DIR = /dls_sw/work/common/python/test/packages
SCRIPT_DIR = /dls_sw/work/common/python/test/scripts
MODULEVER = 0.0

# Override with any release info
-include Makefile.private

# uic files
PYUIC=$(PREFIX)/bin/pyuic4
UICS=$(patsubst %.ui, %_ui.py, $(wildcard dls_pmaccontrol/*.ui))

# build the screens from .ui source
%_ui.py: %.ui
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
		--install-dir=$(INSTALL_DIR) \
		--script-dir=$(SCRIPT_DIR) dist/*.egg        
