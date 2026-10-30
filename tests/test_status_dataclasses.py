from dataclasses import asdict

import pytest

from dls_pmac_control.status_dataclasses import (
    ControllerStatus,
    CurrentCoordinateSystemStatus,
    MotorStatus,
)


def dummy_motor(number=1, **overrides):
    values = {
        "number": number,
        "motor_status": "E40040070401",
        "position": 0.0,
        "velocity": 0.0,
        "following_error": 0.0,
        "i2t_fault_status": False,
        "overcurrent": False,
    }
    values.update(overrides)
    return MotorStatus(**values)


def dummy_brick(motors=None, **overrides):
    values = {
        "identifier_i65": 0,
        "global_status": "202001210800",
        "bus_under_voltage": True,
        "bus_over_voltage": False,
        "over_temp": False,
        "coordinate_systems": CurrentCoordinateSystemStatus(
            cs_status="A80020000000000000",
            feedrate=100.0,
        ),
        "motors": [],
    }

    values.update(overrides)
    return ControllerStatus(**values)
