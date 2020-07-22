dls_pmaccontrol
===========================

The dls_pmaccontrol package is a python application which provides a GUI front end to control the DeltaTau PMAC and Geobrick motor control systems.

Installation
------------

This section describes how to install the module so you can try it out.
For Python modules this often looks like this::

    pip install dls_pmaccontrol

dls_pmaccontrol is developed and tested on Python 2.6. Qt4, PyQt and Qwt5 are used to render the graphical user interface.
These packages must be pre-installed on the system before building and running dls_pmaccontrol.
The dls_pmaclib package is also required for this application. This package is also available on the `Diamond Control Downloads`_ page.

.. _Diamond Control Downloads: http://controls.diamond.ac.uk/downloads/python/index.php

For Mac OS X the following MacPorts_ provide the necessary dependencies:

- py26-pyqt4
- py26-pyqwt
- py26-distribute

.. _MacPorts: http://www.macports.org/ports.php

For Ubuntu (tested on 11.10) the following packages provide the necessary dependencies:

- build-essentials
- pyqt4-dev-tools
- python-qwt5-qt5
- python-setuptools

Once the dependencies are installed, edit the Makefile variables for your platform as suggested in the comments. Finally type make && make install to build and install.

Usage
-----

Run the motor.py to start the application. Connect to PMAC or Geobrick through either Ethernet or Telnet to a terminal server.
