Installation Guide
==================


1. Clone the 2 repos:

* dls-pmac-control.git
* dls-pmac-lib.git

2. Create & activate a Python3 virtual environment:

* dls-python3 -m venv <path-to-virtual-env>
* source venv/bin/activate

3. Build the dls-pmac-lib module:

* Make sure to have an up-to-date version of pip and setuptools:

  * pip install --upgrade pip
  * pip install --upgrade setuptools

* cd dls-pmac-lib
* dls-python3 setup.py clean
* dls-python3 setup.py build
* dls-python3 setup.py install

4. Build the dls-pmac-control module:

* cd dls-pmac-control

* Make the screens:

  * Install pyqt5

    * pip install pyqt5-tools

  * Make  
 
    * make clean
    * make

* Build the module:

  * dls-python3 setup.py clean
  * dls-python3 setup.py build
  * dls-python3 setup.py install


5. Run the application from within the virtual environment:

* dls-pmac-control.py
