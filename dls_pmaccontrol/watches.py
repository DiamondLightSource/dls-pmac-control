# -*- coding: utf-8 -*-

import re
import sys

from formWatches import formWatches
from pmactelnet import PmacTelnetInterface
from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QApplication, QMessageBox, QObject

# [STATE] This should only support displaying integer decimal i-variables at the
# moment, nothing more.

# [IDEA] Possibly use M-variable address definitions to check length of the variable
# [QUES] Is there any reasonable automated way of determining type and length of a
#       variable? Ulrik says if a variable is a "hex type" it will always return as a
#       hex number, even though I wrote an dec int value to it. Or maybe it will
#       not even accept a non-hex value? Clarify this using real test PMAC.
# [TODO] Extend allowed variables to include P and Q variables
# [TODO] M variables may be up to 6 bytes (48 bits) long. I think this is only when
#       they are floats -- but if this can happen even for a non-float situation,
#       then I should extend my bit-flip array to 48 bits long
# [TODO] Make sure variable types are not changed when writing to the PMAC
# [TODO] Use a real PMAC
# [TODO] Add support for floats
#        . Security mask should be usable and restrictive only with integers
# [TODO] Setting values and reflect changes to PMAC
# [TODO] Add continuous polling & warnings when value being edited has changed in
#       the meantime (could use row colouring just like in dls-dependency-checker)


def intToHexPmacFormatted(i):
    assert type(i) in [int]
    str = hex(i)  # e.g. str becomes "0xfa3"
    return "$" + str[2:].upper()  # make that into "$FA3"


def hexPmacFormattedToInt(s):
    assert type(s) is str
    isValid = re.match(r"^\$[0-9a-fA-F]+$", s) is not None
    if not isValid:
        raise ValueError(
            'String "%s" is not in PMAC hex format (use formatting as in "$4FA")'
        )
    i = int(s[1:], 16)  # use base 16 for the conversion to int
    return i


def int2bin(i):
    """Oddly enough, I havent found a simple Python function or formatter to convert
    from integers to binary numbers. So this does the job. can handle signed integers
    as many as 128 bits long."""
    print(
        "int2bin: Would be nice if there were optional spacers between groups of 4 \
        contiguous bits"
    )
    if i == 0:
        return "0"
    if i < 0:
        sign = "-"
        i = -i
    else:
        sign = ""
    mask = 1
    j = 0
    s = ""
    while mask <= i:
        s = str((i & mask) >> j) + s
        j += 1
        mask = 1 << j
    return sign + s


# Converts a string like '1200' or '$94fa' into int, using the appropriate radix;
# converts a string like '-0.234' into a float
def parsePMACFormatValue(s):
    assert type(s) is str
    if s[0:1] == "$":
        return int(s[1:], 16)
    elif s[0:1] == "-$":
        return -int(s[2:], 16)
    elif s.find(".") is -1:
        return int(s)
    else:
        return float(s)


class WatchesForm(formWatches):
    def __init__(self, model, parent=None, name=None, modal=0, fl=0):
        formWatches.__init__(self, parent, name, modal, fl)
        self.model = model

    def addWatch(self):
        print("addWatch()")

        varName = str(self.lneVariableName.text())

        try:
            self.model.addWatch(varName)
        except ValueError as e:
            QMessageBox.information(self, "Cannot create watch", str(e))
            return

        noRows = self.table.numRows()

        self.table.setNumRows(noRows + 1)  # add a new row
        self.table.setText(
            noRows, 0, varName
        )  # set variable name column of the new row
        self.updateWatch(noRows)  # update the watch at the new row

        self.lneVariableName.setText("")

    def updateWatch(self, row):
        varName = str(self.table.text(row, 0))
        try:
            watch = self.model.getWatch(varName)
            if isinstance(watch, IVariableWatch):
                self.table.setText(row, 1, "N/A")
                self.table.setText(row, 2, watch.getVariableValueStr())
        except ValueError:
            self.table.setText(row, 1, "N/A")
            self.table.setText(row, 2, "Error")

    def updateCurrentWatch(self):
        row = self.table.currentRow()
        print("updateCurrentWatch(): current row is %d" % row)
        if row >= 0:
            self.updateWatch(row)

    def removeWatch(self):
        row = self.table.currentRow()
        assert type(row) is int
        print(row)
        if row > -1:
            varName = str(self.table.text(row, 0))
            try:
                self.model.removeWatch(varName)  # remove the watch
                self.table.removeRow(row)
                self.updateEditWatchPanel()
            except ValueError as e:
                QMessageBox.information(self, "Cannot remove watch", str(e))

    def clickTable(self, row, column):
        print("clickTable(%d,%d)" % (row, column))
        self.updateEditWatchPanel()

    def selectedVarName(self):
        currRow = self.table.currentRow()
        if currRow is -1:
            return None
        else:
            return str(self.table.text(currRow, 0))

    def setBitBoxesEnabled(self, isEnabled):
        for i in range(32):
            checkBox = self.__dict__["cb" + str(i)]
            checkBox.setEnabled(isEnabled)

    def updateEditWatchPanel(self):
        if not self.selectedVarName():
            self.panelEditWatch.setEnabled(False)
        else:
            self.panelEditWatch.setEnabled(True)
            watch = self.model.getWatch(self.selectedVarName())
            if isinstance(watch, IVariableWatch):
                # leave only the edit line edit enabled; disable the bit fields
                self.labelEditValue.setEnabled(True)
                self.lneEditValue.setEnabled(True)
                self.setBitBoxesEnabled(False)
                # set the edit line edit's text
                self.lneEditValue.setText(watch.getVariableValueStr())

    def applyEditWatch(self):
        print("applyEditWatch()")
        watch = self.model.getWatch(self.selectedVarName())
        if isinstance(watch, IVariableWatch):
            try:
                newValueStr = str(self.lneEditValue.text())
                print(newValueStr, type(newValueStr))
                watch.setVariableValue(newValueStr)
                self.updateCurrentWatch()
            except (ValueError, IOError) as e:
                QMessageBox.information(self, "Cannot change value", str(e))


class WatchesModel:
    def __init__(self, pmac):
        self.pmac = pmac
        self._watches = {}  # keyed by variable names

    def addWatch(self, varName):
        assert type(varName) is str

        varName = varName.lower()

        isValidPMACVariableName = re.match(r"^i(\d)+$", varName) is not None
        if not isValidPMACVariableName:
            raise ValueError('"%s" is not an accepted PMAC variable name' % varName)
        if varName in self._watches:
            raise ValueError("There is already a watch for this variable")

        isIVariable = re.match(r"^i(\d)+$", varName) is not None
        if isIVariable:
            watch = IVariableWatch(self.pmac, varName)
            self._watches[varName] = watch

        print(self._watches)

    def removeWatch(self, varName):
        print("WatchModel.removeWatch(%s) called" % varName)
        varName = varName.lower()
        print(self._watches.keys())
        try:
            del self._watches[varName]
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        print(self._watches)

    def getWatch(self, varName):
        varName = varName.lower()
        try:
            watch = self._watches[varName]
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        return watch


class Watch:
    def __init__(self, pmac, varName):
        print("Watch.__init__() began.")
        self.varName = varName
        self.pmac = pmac
        # self.isHex = None
        # None here, but do set it in the constructor in child classes

        # Test that at least initially there is no problem reading variable value from
        # the PMAC
        self.getVariableValue()
        print("Watch.__init__() finished.")

    def _sendPMACCommand(self, command):
        """Send a command to PMAC.
        On success, returns a string with response from the PMAC.
        On I/O failure, or if PMAC returns an ERRxx, throws an exception."""
        # Get response from PMAC; the 2nd returned boolean indicates absence of timeout
        (s, wasNoTimeout) = self.pmac.sendCommand(command)
        if not wasNoTimeout:
            raise IOError("Connection to PMAC timed out")

        # Check whether PMAC doesn't reply with an ERRxx type response
        matchObject = re.match(r"^\x07(ERR\d+)\r$", s)
        if matchObject:
            raise ValueError(
                'PMAC error code "%s" while retrieving "%s"'
                % (matchObject.group(1), self.varName)
            )

        # Check whether PMAC replies with a simple '\x06' (basically an "Okay")
        if s == "\x06":
            return ""

        # Remove trailing terminator from PMAC response
        matchObject = re.match(r"^(.*)\r\x06$", s)
        if matchObject:
            return matchObject.group(1)
        else:
            raise ValueError("String returned from PMAC is not correctly terminated")

    def getVariableValueStr(self):
        """Returns a str, containing PMAC formatted value (e.g. "12" or "12.3" or
        "$AF04")."""
        print("Watch.getVariableValueStr()")
        return self._sendPMACCommand(self.varName)

    def getVariableValue(self):
        """Returns an int/long/float (Python types) depending on context.
        For hexadecimal variables, still returns an int with corresponding value."""
        print("Watch.getVariableValue()")
        valueStr = self.getVariableValueStr()
        return parsePMACFormatValue(valueStr)

    def setVariableValue(self, newValue):
        """Attempts to set the new variable value.
        newValue may be either a str being a PMAC-formatted string or one of
        (int, long, float), in which case perform conversion as well.
        Throws exception on failure:
        this may be because newValue is not of appropriate Python type."""
        raise NotImplementedError()


class IVariableWatch(Watch):
    def __init__(self, pmac, varName):

        # Call parent class's constructor
        Watch.__init__(self, pmac, varName)

    # Get variable value to check whether it is hexadecimal, store that in isHex
    # 		rawStrValue = self._sendPMACCommand(varName)
    # 		assert len(rawStrValue) > 0
    # 		self.isHex = rawStrValue[0] is '$'

    def setVariableValue(self, newValue):
        print("IVariableWatch.setVariableValue()")
        assert type(newValue) in (str, int, float)
        self._sendPMACCommand("%s=%s" % (self.varName, str(newValue)))


class MVariableWatch(Watch):
    def __init__(self, pmac, varName):

        # If called with Nonetype parameters, skip the normal initialization.
        # For unit testing purposes only.
        if pmac is None and varName is None:
            return

        # Call parent class's constructor
        Watch.__init__(self, pmac, varName)

        # Parse address definition of the variable; this sets flags:
        # self.signed, self.width, self.floatingPoint.
        definitionStr = self._sendPMACCommand("%s->" % self.varName)
        self._parseAddressDefinition(definitionStr)

    def _parseAddressDefinition(self, definitionStr):
        # Talk to the PMAC and figure out what the variable address definition is.
        # We are interested in these booleans:
        # * signed vs. unsigned
        # * width (no of bits)
        # * fixed vs. floating point

        # Set definition flags to defaults.
        self.signed = False
        self.width = 1
        self.floatingPoint = False

        # This is a special case of the next regex (read its comment first)
        # but with an offset of 24, which means "use all 24 bits and the offset is 0".
        matchObject = re.match(
            r"^([XY])\:?(\$?[0-9a-fA-F]+)\,24(\,([US]))?$", definitionStr
        )
        if matchObject:
            self.width = 24
            # the variable is signed when "S" is present, otherwise
            # (either no letter, or a "U") the variable is unsigned
            self.signed = (
                matchObject.group(4) is not None and matchObject.group(4) == "S"
            )
            return matchObject

        # A "short" variable, up to 24 bits long, using only one of 2 memory banks
        # (X and Y):
        #    Mxxx->bank(:)addr(,offset(,width(,format)))  -- here () means "optional"
        # The banks can be "X" or "Y" and accepted formats are "U" (unsigned, default)
        # or "S" (signed, 2's complement)
        # The offset here can be 0..23, or a special value of 24 -- see next regex
        # The width can be from the set {1, 4, 8, 12, 16, 20, 24}
        matchObject = re.match(
            r"([XY])\:?(\$?[0-9a-fA-F]+)(\,(\d+)(\,(\d+)(\,([SU]))?)?)?", definitionStr
        )
        if matchObject:
            if matchObject.group(6):
                self.width = int(matchObject.group(6))
            # the variable is signed when "S" is present, otherwise
            # (either no letter, or a "U") the variable is unsigned
            self.signed = (
                matchObject.group(8) is not None and matchObject.group(4) == "S"
            )
            return matchObject

        # Select a 48-bit floating-point variable (uses 32 of memory X and 16 bits of
        # memory Y at that address)
        #    Mxxx->L(:)addr
        matchObject = re.match(r"(L)\:?(\$?[0-9a-fA-F]+)", definitionStr)
        if matchObject:
            self.width = 48
            self.signed = True
            self.floatingPoint = True
            return matchObject

        # Select a 48-bit fixed-point signed (2's complement) variable (uses 32 of
        # memory X and 16 bits of memory Y at that address)
        #    Mxxx->D(:)addr
        matchObject = re.match(r"(D)\:?(\$?[0-9a-fA-F]+)", definitionStr)
        if matchObject:
            self.width = 48
            self.signed = True
            return matchObject

        # If the definition did not match any of the regexes, reset variable
        # definition flags and raise an exception.
        # One typical case when this will happen is when the definition is simply "*".
        self.signed = None
        self.width = None
        self.floatingPoint = None
        raise ValueError(
            'Address definition "%s" for M-variable "%s" is not supported'
            % (definitionStr, self.varName)
        )

    def setVariableValue(self, newValue):
        # accepts either a PMAC-formatted string, or int/long/float. however,
        # checks whether the value is in range that is accepted by the PMAC.
        # note: PMAC alone does not complain when the new value's bit length is too long
        # (ignores MSBs)
        pass

    def getBitLength(self):
        # to be used by the viewer
        pass


if __name__ == "__main__":

    # Define unit tests (at least a few -- better than nothing).
    # Call this function, on an open PMAC connection.
    # Failing tests just cause warnings, they don't stop the application from starting.
    def runTests(pmac):
        def doesIVariableWatchReadValue():
            w = IVariableWatch(pmac, "i1000")
            val = w.getVariableValue()
            assert type(val) in (int, float)

        def doesParseMVarAddressDefXY24BitWide():
            w = MVariableWatch(None, None)  # construct a dummy watch
            matchObject = w._parseAddressDefinition("X:$71D,24,S")
            assert matchObject is not None
            print(w.signed, w.width, w.floatingPoint)
            assert w.signed is True and w.width == 24 and w.floatingPoint is False

            matchObject = w._parseAddressDefinition("X:$71D,24")
            assert matchObject is not None
            assert w.signed is False and w.width == 24 and w.floatingPoint is False

        def doesParseMVarAddressDefXYVariousWidth():
            w = MVariableWatch(None, None)  # construct a dummy watch
            matchObject = w._parseAddressDefinition("Y:$078400,10")
            assert matchObject is not None
            assert w.signed is False and w.width == 1 and w.floatingPoint is False
            matchObject = w._parseAddressDefinition("Y:$078402,8,16,U")
            assert matchObject is not None
            assert w.signed is False and w.width == 16 and w.floatingPoint is False
            matchObject = w._parseAddressDefinition("Y:$078404,8,4")
            assert matchObject is not None
            assert w.signed is False and w.width == 4 and w.floatingPoint is False

        def doesParseMVarAddressDef48BitWideSignedInt():
            w = MVariableWatch(None, None)  # construct a dummy watch
            matchObject = w._parseAddressDefinition("D:$000388")
            assert matchObject is not None
            assert w.signed is True and w.width == 48 and w.floatingPoint is False

        def doesParseMVarAddressDef48BitWideFloat():
            w = MVariableWatch(None, None)  # construct a dummy watch
            matchObject = w._parseAddressDefinition("L:$00044F")
            assert matchObject is not None
            assert w.signed is True and w.width == 48 and w.floatingPoint is True

        def doesMVariableWatchInitialise():
            w = MVariableWatch(pmac, "m1")
            assert w.signed is False and w.width == 1 and w.floatingPoint is False

        tests = [
            doesIVariableWatchReadValue,
            doesParseMVarAddressDefXY24BitWide,
            doesParseMVarAddressDefXYVariousWidth,
            doesParseMVarAddressDef48BitWideSignedInt,
            doesParseMVarAddressDef48BitWideFloat,
            doesMVariableWatchInitialise,
        ]

        print("------- Unit tests begin here -------")
        for test in tests:
            try:
                test()
            except AssertionError:
                print('!!! Test "%s" is failing!' % test.__name__)
        print("--------- End of unit tests ---------")

    app = QApplication(sys.argv)
    QObject.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))

    pmac_ts5 = PmacTelnetInterface(verbose=True)
    pmac_ts5.hostname = "ts5"
    pmac_ts5.port = 7003

    connectionErrorMsg = pmac_ts5.connect()
    if connectionErrorMsg:
        print(connectionErrorMsg)
    else:
        runTests(pmac_ts5)
        # run some unit tests (not exhaustive at all) using the
        # open interface to the PMAC

        model = WatchesModel(pmac_ts5)
        window = WatchesForm(model)
        app.setMainWidget(window)
        window.show()
        app.exec_loop()

        pmac_ts5.disconnect()
