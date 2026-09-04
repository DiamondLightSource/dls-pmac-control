from dataclasses import dataclass, field


@dataclass
class MotorStatus:
    number: int
    motor_status: str
    position: float
    velocity: float
    following_error: float
    i2t_fault_status: float
    overcurrent: float | None = None


@dataclass
class CurrentCoordinateSystemStatus:
    cs_status: str
    feedrate: float
    bus_under_voltage: bool | None = None
    bus_over_voltage: bool | None = None
    over_temp: bool | None = None


@dataclass
class ControllerStatus:
    identifier_i65: int
    global_status: str
    coordinate_systems: CurrentCoordinateSystemStatus
    motors: list[MotorStatus] = field(default_factory=list)
