"""International Standard Atmosphere (ISA) model, sea level to 51 km.

Altitudes are geopotential altitudes in metres, which is how the ISA
tables are defined. Use ``geometric_to_geopotential`` and
``geopotential_to_geometric`` to convert between the two; at 11 km the
difference is about 19 m, small but not zero.

The layer structure, lapse rates, and sea-level references follow the
ISO 2533 / ICAO standard atmosphere. Within each layer, temperature is
either linear in altitude (a gradient layer) or constant (an isothermal
layer), and pressure follows from hydrostatic equilibrium with the ideal
gas law. Layer base pressures are propagated from the sea-level value, so
temperature and pressure are continuous across layer boundaries by
construction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Sea-level reference values (ISA definition).
T0_K = 288.15
P0_PA = 101325.0
RHO0_KG_M3 = 1.225

# Physical constants.
G0_M_S2 = 9.80665
R_SPECIFIC = 287.05287  # J/(kg K), dry air
GAMMA = 1.4
EARTH_RADIUS_M = 6356766.0  # m, used for the geopotential conversion

# Sutherland constants for the dynamic viscosity of air.
SUTHERLAND_BETA = 1.458e-6  # kg/(m s sqrt(K))
SUTHERLAND_S_K = 110.4  # K

# Highest altitude covered by the model (top of the fourth ISA layer).
MAX_ALTITUDE_M = 51000.0

# ISA layers as (base altitude m, base temperature K, lapse rate K/m),
# ordered by base altitude. The temperature at the top of one layer is the
# base temperature of the next.
_LAYERS = (
    (0.0, 288.15, -0.0065),      # troposphere
    (11000.0, 216.65, 0.0),      # tropopause / lower stratosphere
    (20000.0, 216.65, 0.001),    # stratosphere, warming
    (32000.0, 228.65, 0.0028),   # stratosphere, warming faster
    (47000.0, 270.65, 0.0),      # stratopause, isothermal to 51 km
)


def _layer_base_pressures() -> tuple[float, ...]:
    """Propagate sea-level pressure up to each layer base."""
    pressures = [P0_PA]
    for i in range(1, len(_LAYERS)):
        hb_prev, tb_prev, lapse_prev = _LAYERS[i - 1]
        hb, tb, _lapse = _LAYERS[i]
        dh = hb - hb_prev
        if lapse_prev == 0.0:
            p = pressures[-1] * math.exp(-G0_M_S2 * dh / (R_SPECIFIC * tb_prev))
        else:
            p = pressures[-1] * (tb / tb_prev) ** (-G0_M_S2 / (lapse_prev * R_SPECIFIC))
        pressures.append(p)
    return tuple(pressures)


_LAYER_BASE_PRESSURES = _layer_base_pressures()


def _layer_index(altitude_m: float) -> int:
    """Index of the ISA layer containing the given geopotential altitude."""
    if not 0.0 <= altitude_m <= MAX_ALTITUDE_M:
        raise ValueError(
            f"altitude {altitude_m} m is outside the ISA model range "
            f"0 to {MAX_ALTITUDE_M:.0f} m"
        )
    idx = 0
    for i, (base, _t, _lapse) in enumerate(_LAYERS):
        if altitude_m >= base:
            idx = i
    return idx


def geometric_to_geopotential(altitude_m: float) -> float:
    """Convert geometric altitude (above sea level) to geopotential altitude."""
    return EARTH_RADIUS_M * altitude_m / (EARTH_RADIUS_M + altitude_m)


def geopotential_to_geometric(altitude_m: float) -> float:
    """Convert geopotential altitude back to geometric altitude."""
    return EARTH_RADIUS_M * altitude_m / (EARTH_RADIUS_M - altitude_m)


def temperature(altitude_m: float) -> float:
    """ISA temperature in kelvin at the given geopotential altitude."""
    hb, tb, lapse = _LAYERS[_layer_index(altitude_m)]
    return tb + lapse * (altitude_m - hb)


def pressure(altitude_m: float) -> float:
    """ISA pressure in pascals at the given geopotential altitude."""
    idx = _layer_index(altitude_m)
    hb, tb, lapse = _LAYERS[idx]
    pb = _LAYER_BASE_PRESSURES[idx]
    dh = altitude_m - hb
    if lapse == 0.0:
        return pb * math.exp(-G0_M_S2 * dh / (R_SPECIFIC * tb))
    t = tb + lapse * dh
    return pb * (t / tb) ** (-G0_M_S2 / (lapse * R_SPECIFIC))


def density(altitude_m: float) -> float:
    """ISA air density in kg/m^3 at the given geopotential altitude."""
    return pressure(altitude_m) / (R_SPECIFIC * temperature(altitude_m))


def speed_of_sound(altitude_m: float) -> float:
    """Speed of sound in m/s at the given geopotential altitude."""
    return math.sqrt(GAMMA * R_SPECIFIC * temperature(altitude_m))


def dynamic_viscosity(altitude_m: float) -> float:
    """Dynamic viscosity in Pa s at the altitude, from Sutherland's formula."""
    t = temperature(altitude_m)
    return SUTHERLAND_BETA * t ** 1.5 / (t + SUTHERLAND_S_K)


@dataclass(frozen=True)
class AtmosphereState:
    """The full ISA state at one altitude."""

    altitude_m: float
    temperature_k: float
    pressure_pa: float
    density_kg_m3: float
    speed_of_sound_m_s: float
    dynamic_viscosity_pa_s: float

    @property
    def temperature_c(self) -> float:
        return self.temperature_k - 273.15


def state(altitude_m: float) -> AtmosphereState:
    """Return every ISA property at the given geopotential altitude."""
    return AtmosphereState(
        altitude_m=altitude_m,
        temperature_k=temperature(altitude_m),
        pressure_pa=pressure(altitude_m),
        density_kg_m3=density(altitude_m),
        speed_of_sound_m_s=speed_of_sound(altitude_m),
        dynamic_viscosity_pa_s=dynamic_viscosity(altitude_m),
    )
