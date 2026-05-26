#!/bin/env/python2.6
WORD = 24
LONGWORD = 48
# initialise the data addresses that the PMAC can gather from
motor_base_addrs = [
    0x080,
    0x100,
    0x180,
    0x200,
    0x280,
    0x300,
    0x380,
    0x400,
    0x480,
    0x500,
    0x580,
    0x600,
    0x680,
    0x700,
    0x780,
    0x800,
    0x880,
    0x900,
    0x980,
    0xA00,
    0xA80,
    0xB00,
    0xB80,
    0xC00,
    0xC80,
    0xD00,
    0xD80,
    0xE00,
    0xE80,
    0xF00,
    0xF80,
    0x1000,
]

pmac_data_sources = [
    {
        "reg": 0x08,
        "desc": "Motor present desired position",
        "unit": "[cts]",
        "size": 0x8,
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",),
    },
    {
        "reg": 0x0B,
        "desc": "Motor present actual position",
        "unit": "[cts]",
        "size": 0x8,
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",),
    },
    {
        "reg": 0x11,
        "desc": "Motor following error",
        "unit": "[cts]",
        "size": 0x8,
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",),
    },
    {
        "reg": 0x1D,
        "desc": "Motor present actual velocity (unfiltered)",
        "unit": "[cts/servo cycle]",
        "size": 0x4,
        "scalingCalc": "1.0/(%d*32.0)/(%d+1)",
        "scalingIvars": ("i%d09", "i%d60"),
    },
]

ppmac_data_sources = [
    {
        "desc": "Motor present desired position",
        "unit": "[cts]",
        "addr": "DesPos.a",
    },
    {
        "desc": "Motor present actual position",
        "unit": "[cts]",
        "addr": "ActPos.a",
    },
    {
        "desc": "Motor following error",
        "unit": "[cts]",
        "addr": "PosError.a",
    },
    {
        "desc": "Motor present actual velocity (unfiltered)",
        "unit": "[cts/servo cycle]",
        "addr": "ActVel.a",
    },
]


class PpmacGatherChannel:
    def __init__(self, pmac, qwt_curve):
        self.pmac = pmac
        self.qwtCurve = qwt_curve
        self.axisNo = None
        self.descNo = None


class PmacGatherChannel:
    def __init__(self, pmac, qwt_curve):
        self.axisNo = None
        self.pmac = pmac

        # Define the data arrays that each channel will maintain
        self.strData = []
        self.rawData = []
        self.scaledData = []

        # Data source I variable (5001-5048)
        # and data source address
        self.pSrcIvar = None
        self.srcDataAddr = ""

        # Information about the data
        self.dataWidth = None  # How many bits wide
        self.dataType = None  # float or int
        self.regOffset = None  # The data offset from the motor base address
        # (i.e. what the data represents physically: pos, velo, foll. osv osv)
        self.dataSourceInfo = None  # data source dict (from global dataSources)

        self.scalingFactor = None

        self.qwtCurve = qwt_curve

    def set_data_gather_pointer(self, ivar):
        self.pSrcIvar = ivar
        return

    # Read the address of a gather I variable and interpret the
    # address to determine: datawidth, datatype, unit and scaling factor
    # result is returned in a dictionary
    def get_data_info(self):
        # read the gather I variable from the pmac
        (ret_str, status) = self.pmac.sendCommand(self.pSrcIvar)
        if not status:
            return None

        # Get the data width and type from the first digit in the hex-value
        len_word = ret_str.strip("$")[0]
        if len_word == "0" or len_word == "4":
            self.dataWidth = WORD
            self.dataType = int
        elif len_word == "8":
            self.dataWidth = LONGWORD
            self.dataType = int
        elif len_word == "C":
            self.dataWidth = LONGWORD
            self.dataType = float
        else:
            print(f"### Error: Could not get data width and type from: {ret_str}")

        # Figure out what data the address point to
        data_addr = int(ret_str[2:-1], 16)
        self.regOffset = 0x7F & data_addr

        # Figure out what axis we are looking at
        m_base_addr = data_addr & 0xFFF80
        try:
            self.axisNo = motor_base_addrs.index(m_base_addr) + 1
        except Exception:
            print(f"### Error: could not recognise motor base address: {m_base_addr:X}")

        # Get the data source info (unit, scaling algorithm and so on)
        for data_src in pmac_data_sources:
            if data_src["reg"] == self.regOffset:
                self.dataSourceInfo = data_src
                break
        if not self.dataSourceInfo:
            print(
                f"### Error: could not recognise data source type with reg offset: {self.regOffset:X}"
            )
        return

    # Receive the array of strings straight from the source
    def set_str_data(self, str_data):
        self.strData = str_data
        return

    # Convert the array of hexadecimal strings to int or float arrays
    def str_to_raw(self):
        # if we have no data yet, return with error
        if not (len(self.strData) > 0):
            return False

        # Check the data width to be able to make a proper conversion
        # from string to signed integer/float
        if self.dataWidth == LONGWORD:
            sign_mask = 0x800000000000
            max_value = 0xFFFFFFFFFFFF
        elif self.dataWidth == WORD:
            sign_mask = 0x800000
            max_value = 0xFFFFFF
        else:
            print(
                f"### Error: did not have valid data width information (had {self.dataWidth})"
            )
            return None

        # convert each hex string value to an integer with sign
        self.rawData = []
        for str_data_point in self.strData:
            val = int(str_data_point, 16)
            if val & sign_mask:
                val -= max_value
            self.rawData.append(val)
        return

    def get_scaling_factor(self):
        # if a scaling algorithm doesn't exist we just set scaling factor to 1
        if "scalingCalc" not in self.dataSourceInfo:
            self.scalingFactor = 1.0
            return

        # Get the necessary I variable factors from the pmac
        ivar_factors = []
        for part_ivar in self.dataSourceInfo["scalingIvars"]:
            ivar = part_ivar % self.axisNo
            (ret_str, status) = self.pmac.sendCommand(ivar)
            if not status:
                print(f"### Error: did not receive response to: {ivar}")
                return None
            # if hex value...
            if ret_str[0] == "$":
                ivar_factor = int(ret_str.strip("$"), 16)
            else:
                ivar_factor = float(ret_str[:-1])
            ivar_factors.append(ivar_factor)

        # calculate the final scaling factor from the ivar factors
        # and the algorithm as described in the pmac manual
        ivar_factors = tuple(ivar_factors)
        algorithm = self.dataSourceInfo["scalingCalc"] % ivar_factors
        # print "Evaluating algorithm: %s"%( algorithm )
        try:
            self.scalingFactor = eval(algorithm)
        except Exception:
            print(
                f"### Error: did not evaluate expression correctly. Expr: {algorithm}"
            )
            return None

        return

    def raw_to_scaled(self):
        if not self.scalingFactor:
            self.get_scaling_factor()
        if not self.rawData:
            print("### Error: No raw data available to scale.")
            return None
        if not self.scalingFactor:
            self.scaledData = self.rawData
            return None

        self.scaledData = []
        for raw_val in self.rawData:
            self.scaledData.append(raw_val * self.scalingFactor)
        return
