#!/bin/env/python2.6
WORD = 24
LONGWORD = 48
# initialise the data addresses that the PMAC can gather from
motorBaseAddrs = []

dataSources = [
    {
        "desc": "Motor present desired position",
        "unit": "[cts]",
        "addr": "DesPos.a",
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",)
    },
    {
        "desc": "Motor present actual position",
        "unit": "[cts]",
        "addr": "ActPos.a",
        "size": 0x8,
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",)
    },
    {
        "desc": "Motor following error",
        "unit": "[cts]",
        "addr": "PosError.a",
        "size": 0x8,
        "scalingCalc": "1.0/(%d*32.0)",
        "scalingIvars": ("i%d08",)
    },
    {
        "desc": "Motor present actual velocity (unfiltered)",
        "unit": "[cts/servo cycle]",
        "addr": "ActVel.a",
        "size": 0x4,
        "scalingCalc": "1.0/(%d*32.0)/(%d+1)",
        "scalingIvars": ("i%d09", "i%d60")
    },
]

class GatherChannel:
    def __init__(self, pmac, qwtCurve):
        self.axisNo = None
        self.pmac = pmac

        # Define the data arrays that each channel will maintain
        self.strData = []
        self.rawData = []
        self.scaledData = []

        # Information about the data
        self.dataWidth = None  # How many bits wide
        self.dataType = None  # float or int

        self.dataSourceInfo = None  # data source dict (from global dataSources)

        self.scalingFactor = None

        self.qwtCurve = qwtCurve

    # Receive the array of strings straight from the source
    def setStrData(self, strData):
        self.strData = strData
        return

    # Convert the array of strings to int or float arrays
    def strToRaw(self):
        # if we have no data yet, return with error
        if not (len(self.strData) > 0):
            return False

        else:
            return 0

    def getScalingFactor(self):
        # if a scaling algorithm doesn't exist we just set scaling factor to 1
        if "scalingCalc" not in self.dataSourceInfo:
            self.scalingFactor = 1.0
            return


    def rawToScaled(self):
        if not self.scalingFactor:
            self.getScalingFactor()
        if not self.rawData:
            print("### Error: No raw data available to scale.")
            return None
        if not self.scalingFactor:
            self.scaledData = self.rawData
            return None

        self.scaledData = []
        for rawVal in self.rawData:
            self.scaledData.append(rawVal * self.scalingFactor)
        return
