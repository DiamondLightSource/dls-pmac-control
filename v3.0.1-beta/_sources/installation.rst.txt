Installation Guide
==================

1. Clone the 2 repos:

* dls-pmac-control.git

* dls-pmac-lib.git

2. Create & activate a Python3 virtual environment:

.. code-block:: console

   dls-python3 -m venv <path-to-virtual-env>

   source venv/bin/activate

3. Make sure to have an up-to-date version of pip and setuptools:

.. code-block:: console

   pip install --upgrade pip

   pip install --upgrade setuptools

4. Build the dls-pmac-lib module:

.. code-block:: console

  cd dls-pmac-lib

  dls-python3 setup.py clean

  dls-python3 setup.py build

  dls-python3 setup.py install

5. Install pyqt5:

.. code-block:: console

  cd dls-pmac-control

  pip install pyqt5-tools

6. Make the screens:

.. code-block:: console

  make clean

  make

7. Build the dls-pmac-control module:

.. code-block:: console

  dls-python3 setup.py clean

  dls-python3 setup.py build

  dls-python3 setup.py install

8. Run the application from within the virtual environment:

.. code-block:: console

  dls-pmac-control.py
