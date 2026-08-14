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
    # number: int
    # running: bool
    # in_position: bool
    identifier_i65: int
    global_status: str
    cs_status: str
    feedrate: float


@dataclass
class ControllerStatus:
    # global_status: str
    coordinate_systems: list[CurrentCoordinateSystemStatus] = field(default_factory=list)
    motors: list[MotorStatus] = field(default_factory=list)
