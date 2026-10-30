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
        "motors": [] if motors is None else motors,
    }

    values.update(overrides)
    return ControllerStatus(**values)


class TestMotorStatus:
    def test_motor_values(self):
        motor = dummy_motor()

        assert motor.number == 1
        assert motor.motor_status == "E40040070401"
        assert motor.position == 0.0
        assert motor.velocity == 0.0
        assert motor.following_error == 0.0
        assert motor.i2t_fault_status is False
        assert motor.overcurrent is False


class TestCurrentCoordinateSystemStatus:
    def test_ccs_values(self):
        css_status = CurrentCoordinateSystemStatus(
            cs_status="A80020000000000000",
            feedrate=100.0,
        )

        assert css_status.cs_status == "A80020000000000000"
        assert css_status.feedrate == 100.0


class TestControllerStatus:
    def test_controller_values(self):
        motor = dummy_motor()

        status = dummy_brick(motors=[motor])

        assert status.identifier_i65 == 0
        assert status.global_status == "202001210800"
        assert status.bus_under_voltage is True
        assert status.bus_over_voltage is False
        assert status.over_temp is False

        assert status.motors == [motor]
        assert status.motors[0].position == 0.0
