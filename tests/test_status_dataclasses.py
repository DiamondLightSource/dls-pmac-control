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
