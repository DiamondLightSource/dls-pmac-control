Main GUI Screen
===============

Running the application will launch the following screen:

.. _label-main:
.. figure:: gui_images/main-window-startup.png
  :width: 600
  :alt: Initial GUI screen

  *GUI startup screen*

The user must connect to a PMAC in order to access the various tools provided by the application.

Connection
----------

The user can connect to a PMAC using Telnet, Ethernet, or Serial connection. Connection to a Power PMAC can be achieved via the SSH protocol. 

To connect to the hardware select the connection type and press connect. There is the option of changing the connection parameters if required. 

When connecting via SSH protocol, the default username and password will be used and if this fails then the following screen (:numref:`label-login`) will be shown to promt the user for another username and password:

.. _label-login:

.. figure:: gui_images/login.png
  :width: 400
  :alt: screen to prompt user for SSH authentication

  *Login screen to prompt user for SSH authentication*

A pop-up window will be displayed if the connection fails for the PMAC (:numref:`label-refused`) or Power PMAC (:numref:`label-conn-error`). Examples of these are shown below.

.. _label-refused:

.. figure:: gui_images/refused-connection.png
  :width: 300

  *Pop-up window for connection refused*

.. _label-conn-error:

.. figure:: gui_images/connection-error.png
  :width: 300

  *Pop-up window for connection error*

Upon successfully connecting the application will launch a screen similar to the following:

.. _label-connected:

.. figure:: gui_images/pmac-connected.png
  :width: 600
  :alt: GUI screen when first connected

  *GUI immediately after connecting*

The user can now access the screens and features which have been enabled as shown in :numref:`label-connected`.

.. _label-annotated:

.. figure:: gui_images/annotated-gui-main.png
  :width: 600
  :alt: GUI screen with annotation

  *Main GUI screen showing: (1) Connection protocol (2) Axis control (3) Polling window (4) Additional screens (5) Command window*


Jog Ribbon
----------

The jog ribbon can be found within the main screen (:numref:`label-annotated` *(2)*) and allows the user to move individual motors. The jog ribbon also shows the position, velocity, and following error of the current motor and shows LEDs which indicate whether a position limit has been reached. 

.. _label-red:

.. figure:: gui_images/red-hi-lim.png
  :width: 400

  *Red LED indicating motor position limit reached*

.. _label-amber:

.. figure:: gui_images/amber-hi-lim.png
  :width: 400

  *Amber LED indicating software motor position limit reached*


Note that for the Power PMAC these LEDs will be red when hardware limits have been reached and amber when software limits have been reached (see :numref:`label-amber`). LEDs are always red for PMAC (see :numref:`label-red`) as there is no distinction between hardware and software limits.


Axis Settings
-------------

To configure the settings for a particular axis press the "settings..." button in the main screen (:numref:`label-annotated` *(2)*). This will launch the following screen which has two tabs for PMAC models:

.. figure:: gui_images/pmac-axis-settings.png
  :width: 400

  *PMAC Axis Settings (PID and macro variables)*

.. figure:: gui_images/pmac-axis-settings2.png
  :width: 400

  *PMAC Axis Settings (definition and safety variables)*


The values shown on this screen can be edited by typing in new values and pressing enter. This will send a command to the hardware to set the variable to the desired value. It is expected that new values are in a format which can be interpreted by the PMAC and within an allowed range for that variable. Unlike in the polling table, values do not update periodically, instead the user must click update to read back values from the PMAC.

For the Power PMAC the axis settings screen is as follows:

.. _fig-ppmac-settings:

.. figure:: gui_images/power-pmac-axis-settings.png
  :width: 400

  *Power PMAC Axis Settings*

The screen shown in :numref:`fig-ppmac-settings` can be used in the same way as for the PMAC.


Status Screens
--------------

There are three status screens available to the user. One displays motor status items, one shows status items for the coordinate system, and the other shows global status items. This screens will differ slightly for PMAC and Power PMAC. 

To show the motor status screen press the "status..." button (shown in :numref:`label-annotated` *(2)*). Green LEDs will light up to show that the status bit has been set. The user can hover over each status item for a more in depth explanation of what it indicates. 

The coordinate system status and global status screens can be found in the "additional screens" section (*(4)* :numref:`label-annotated`).


Polling
-------

The polling table (:numref:`label-annotated` *(3)*) shows the position, velocity, and following error of all the motors. LEDs which indicate whether a position limit has been reached are also displayed in the table. Note that for the Power PMAC an amber LED indicates a software limit and a red LED indicates a hardware limit.

The polling window is updated periodically by sending a command to the PMAC to request particular values.  

Sending Commands
----------------

The application includes the option to send commands directly to the PMAC using the bar shown in the "command window" in the main window (:numref:`label-annotated` *(5)*). The checkbox labelled "show all commands sent" allows the option of displaying any commands sent by any other parts of the application. For example, when using the jog ribbon, if this box is ticked then any jog commands sent to the controller will be displayed in the command window.


Loading PLCs
------------

The application allows the user to load a PLC line-by-line onto the PMAC. When the "load pmc..." button (found in :numref:`label-annotated` *(4)*) is pressed a window is launched which allows the user to choose a PLC from their local machine. Whilst the PLC is loading a progress bar is displayed. Note that if the PLC cannot be interpreted by the controller then the application may freeze while loading the PLC. 
