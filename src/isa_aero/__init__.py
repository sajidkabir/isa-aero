"""isa-aero: ISA atmosphere and aerodynamics utilities."""

from .atmosphere import (
    AtmosphereState,
    density,
    dynamic_viscosity,
    geometric_to_geopotential,
    geopotential_to_geometric,
    pressure,
    speed_of_sound,
    state,
    temperature,
)
from .aero import (
    cas_to_tas,
    drag_force,
    dynamic_pressure,
    eas_to_tas,
    lift_force,
    mach_number,
    reynolds_number,
    stall_speed,
    tas_to_cas,
    tas_to_eas,
)

__version__ = "1.0.0"

__all__ = [
    "AtmosphereState",
    "cas_to_tas",
    "density",
    "drag_force",
    "dynamic_pressure",
    "dynamic_viscosity",
    "eas_to_tas",
    "geometric_to_geopotential",
    "geopotential_to_geometric",
    "lift_force",
    "mach_number",
    "pressure",
    "reynolds_number",
    "speed_of_sound",
    "stall_speed",
    "state",
    "tas_to_cas",
    "tas_to_eas",
    "temperature",
]
