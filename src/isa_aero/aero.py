"""Basic aerodynamics quantities and airspeed conversions.

Speeds are in m/s, densities in kg/m^3, lengths in m, forces in N.

Equivalent airspeed (EAS) uses the incompressible definition: it is the
sea-level speed that gives the same dynamic pressure, 0.5 * rho * V^2.
Calibrated airspeed (CAS) is defined through the pitot impact pressure
with sea-level standard conditions, so converting between TAS and CAS
accounts for compressibility. The CAS conversions use the subsonic
isentropic relations and are valid below Mach 1; they raise ValueError
above it rather than returning a quietly wrong number.
"""

from __future__ import annotations

import math

from . import atmosphere

_GAMMA = atmosphere.GAMMA
_RHO0 = atmosphere.RHO0_KG_M3
_P0 = atmosphere.P0_PA
_G0 = atmosphere.G0_M_S2


def dynamic_pressure(density_kg_m3: float, speed_m_s: float) -> float:
    """Dynamic pressure q = 0.5 * rho * V^2, in pascals."""
    return 0.5 * density_kg_m3 * speed_m_s ** 2


def reynolds_number(
    density_kg_m3: float,
    speed_m_s: float,
    length_m: float,
    viscosity_pa_s: float,
) -> float:
    """Reynolds number Re = rho * V * L / mu (dimensionless)."""
    return density_kg_m3 * speed_m_s * length_m / viscosity_pa_s


def mach_number(speed_m_s: float, speed_of_sound_m_s: float) -> float:
    """Mach number M = V / a (dimensionless)."""
    return speed_m_s / speed_of_sound_m_s


def tas_to_eas(tas_m_s: float, altitude_m: float) -> float:
    """True airspeed to equivalent airspeed at the given ISA altitude."""
    sigma = atmosphere.density(altitude_m) / _RHO0
    return tas_m_s * math.sqrt(sigma)


def eas_to_tas(eas_m_s: float, altitude_m: float) -> float:
    """Equivalent airspeed to true airspeed at the given ISA altitude."""
    sigma = atmosphere.density(altitude_m) / _RHO0
    return eas_m_s / math.sqrt(sigma)


def _impact_pressure_from_mach(mach: float, pressure_pa: float) -> float:
    """Pitot impact pressure for subsonic flow at the given static pressure."""
    return pressure_pa * ((1.0 + 0.2 * mach ** 2) ** 3.5 - 1.0)


def _mach_from_impact_pressure(impact_pa: float, pressure_pa: float) -> float:
    """Subsonic Mach number from a pitot impact pressure."""
    return math.sqrt(5.0 * ((impact_pa / pressure_pa + 1.0) ** (2.0 / 7.0) - 1.0))


def tas_to_cas(tas_m_s: float, altitude_m: float) -> float:
    """True airspeed to calibrated airspeed at the given ISA altitude.

    Works through the impact pressure: the pitot tube senses one impact
    pressure, and CAS is the sea-level speed that would produce it.
    """
    a = atmosphere.speed_of_sound(altitude_m)
    mach = tas_m_s / a
    if mach >= 1.0:
        raise ValueError(
            "TAS to CAS conversion uses the subsonic pitot relation; "
            f"this speed is Mach {mach:.2f} at {altitude_m:.0f} m"
        )
    impact = _impact_pressure_from_mach(mach, atmosphere.pressure(altitude_m))
    a0 = atmosphere.speed_of_sound(0.0)
    return a0 * _mach_from_impact_pressure(impact, _P0)


def cas_to_tas(cas_m_s: float, altitude_m: float) -> float:
    """Calibrated airspeed to true airspeed at the given ISA altitude."""
    a0 = atmosphere.speed_of_sound(0.0)
    if cas_m_s >= a0:
        raise ValueError(
            "CAS to TAS conversion uses the subsonic pitot relation; "
            "this CAS is at or above the sea-level speed of sound"
        )
    impact = _impact_pressure_from_mach(cas_m_s / a0, _P0)
    p = atmosphere.pressure(altitude_m)
    mach = _mach_from_impact_pressure(impact, p)
    if mach >= 1.0:
        raise ValueError(
            "CAS to TAS conversion uses the subsonic pitot relation; "
            f"this CAS implies Mach {mach:.2f} at {altitude_m:.0f} m"
        )
    return mach * atmosphere.speed_of_sound(altitude_m)


def lift_force(
    cl: float, density_kg_m3: float, speed_m_s: float, wing_area_m2: float
) -> float:
    """Lift in newtons: L = q * S * Cl."""
    return dynamic_pressure(density_kg_m3, speed_m_s) * wing_area_m2 * cl


def drag_force(
    cd: float, density_kg_m3: float, speed_m_s: float, wing_area_m2: float
) -> float:
    """Drag in newtons: D = q * S * Cd."""
    return dynamic_pressure(density_kg_m3, speed_m_s) * wing_area_m2 * cd


def stall_speed(
    mass_kg: float,
    wing_area_m2: float,
    cl_max: float,
    altitude_m: float = 0.0,
    density_kg_m3: float | None = None,
) -> float:
    """Stall speed in m/s: the speed where lift at Cl_max equals weight.

    Vs = sqrt(2 * m * g / (rho * S * Cl_max)). Density comes from the ISA
    model at ``altitude_m`` unless ``density_kg_m3`` is given directly.
    """
    rho = atmosphere.density(altitude_m) if density_kg_m3 is None else density_kg_m3
    return math.sqrt(2.0 * mass_kg * _G0 / (rho * wing_area_m2 * cl_max))
