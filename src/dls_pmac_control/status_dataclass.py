from dataclasses import dataclass, field


@dataclass
class MotorStatus:
    number: int
    position: float
    velocity: float
    following_error: float
    amplifier_status: float


@dataclass
class CoordinateSystemStatus:
    number: int
    running: bool
    in_position: bool
    feedrate: float


@dataclass
class ControllerStatus:
    # global_status: str
    coordinate_systems: list[CoordinateSystemStatus] = field(default_factory=list)
    motors: list[MotorStatus] = field(default_factory=list)
