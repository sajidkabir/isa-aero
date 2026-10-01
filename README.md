# isa-aero

[![CI](https://github.com/sajidkabir/isa-aero/actions/workflows/ci.yml/badge.svg)](https://github.com/sajidkabir/isa-aero/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23077738.svg)](https://doi.org/10.5281/zenodo.23077738)

ISA atmosphere and aerodynamics utilities in pure Python, with no runtime
dependencies. It provides a layered International Standard Atmosphere model
from sea level to 51 km, the everyday aerodynamics quantities built on top
of it (dynamic pressure, Reynolds number, Mach number, lift, drag, stall
speed), and true / equivalent / calibrated airspeed conversions that
account for compressibility.

Every flight calculation starts with the atmosphere: how dense the air is,
how fast sound travels, how thick it feels to a wing. This package is that
starting point, written to be read, checked against the published ISA
tables, and reused. It is the atmosphere layer underneath larger tools
such as [solar-uav-sim](https://github.com/sajidkabir/solar-uav-sim).

## Features

- **Layered ISA model to 51 km**: all five standard layers with their lapse
  rates, from the troposphere through the isothermal tropopause and the
  warming stratosphere to the stratopause.
- **Full state at any altitude**: temperature, pressure, density, speed of
  sound, and dynamic viscosity (Sutherland's formula) from one call.
- **Geopotential altitude conversion**: the ISA tables are defined in
  geopotential altitude; helpers convert to and from geometric altitude.
- **Airspeed conversions**: TAS to EAS (incompressible density correction)
  and TAS to CAS through the pitot impact pressure, so compressibility is
  handled properly. Both directions, both round-trip exactly.
- **Aero helpers**: dynamic pressure, Reynolds number, Mach number, lift
  and drag forces from Cl / Cd, and a stall speed helper.
- **CLI**: `at` prints the full ISA state at an altitude, `convert` turns
  a true airspeed into EAS and CAS at an altitude.
- **No dependencies**: standard library only. It installs anywhere Python
  3.10 or newer runs.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/sajidkabir/isa-aero.git
cd isa-aero
pip install -e .
```

For development (adds the test runner):

```bash
pip install -e . pytest
pytest -q
```

## Quickstart

### Command line

Print the full ISA state at the tropopause, 11 km:

```bash
isa-aero at --altitude 11000
```

```text
ISA state at 11000 m (geopotential)
  Temperature:     216.65 K (-56.50 C)
  Pressure:        22632.0 Pa
  Density:         0.3639 kg/m3
  Speed of sound:  295.07 m/s
  Viscosity:       1.4216e-05 Pa s
```

Convert a true airspeed at that altitude:

```bash
isa-aero convert --tas 250 --altitude 11000
```

```text
Airspeed conversion at 11000 m (ISA)
  TAS:             250.00 m/s (Mach 0.847)
  EAS:             136.26 m/s
  CAS:             145.46 m/s
```

Note the spread: at 11 km a TAS of 250 m/s loads the wing like 136 m/s at
sea level (EAS), while the pitot-based calibrated speed reads higher,
about 145 m/s, because it also carries the compressibility of the air at
Mach 0.85.

### Python API

```python
from isa_aero import density, speed_of_sound, state, tas_to_cas, tas_to_eas

s = state(11000.0)
print(s.temperature_k, s.pressure_pa, s.density_kg_m3)

print(density(5000.0))            # 0.7361 kg/m3
print(speed_of_sound(0.0))        # 340.29 m/s
print(tas_to_eas(250.0, 11000.0)) # EAS at altitude
print(tas_to_cas(250.0, 11000.0)) # CAS at altitude
```

## How it works

| Module | Responsibility |
| --- | --- |
| `atmosphere.py` | Layered ISA model: temperature, pressure, density, speed of sound, viscosity, geopotential conversion |
| `aero.py` | Dynamic pressure, Reynolds and Mach numbers, airspeed conversions, lift, drag, stall speed |
| `cli.py` | Command-line interface |

Key relations:

- Temperature in a gradient layer: T = T_b + L * (h - h_b), with the layer
  lapse rate L (in the troposphere, L = -6.5 K per km)
- Pressure in a gradient layer: p = p_b * (T / T_b) ^ (-g / (L * R))
- Pressure in an isothermal layer: p = p_b * exp(-g * (h - h_b) / (R * T_b))
- Density from the ideal gas law: rho = p / (R * T)
- Speed of sound: a = sqrt(gamma * R * T)
- Viscosity from Sutherland's formula: mu = beta * T^1.5 / (T + S)
- EAS from TAS: V_e = V_t * sqrt(rho / rho_0)
- CAS from TAS via the impact pressure: q_c = p * ((1 + 0.2 * M^2)^3.5 - 1),
  then read as a sea-level speed
- Stall speed: V_s = sqrt(2 * m * g / (rho * S * Cl_max))

Layer base pressures are propagated from the sea-level value rather than
typed in from a table, so temperature and pressure are continuous across
layer boundaries by construction, and the whole model hangs off the single
sea-level definition.

## Validation and sanity checks

The test suite (18 tests) checks the model against the published ISA
tables, not just against itself:

- Sea-level values match the definition: 288.15 K, 101325 Pa, 1.225 kg/m3,
  speed of sound about 340.3 m/s, viscosity about 1.789e-5 Pa s.
- At 11 km the model reproduces the table: 216.65 K, 22632 Pa, 0.36392
  kg/m3, each within a fraction of a percent.
- At 20 km it reproduces 5474.89 Pa and 0.08802 kg/m3 the same way.
- The tropospheric lapse rate is exactly 6.5 K/km and the lower
  stratosphere is isothermal at 216.65 K.
- Density decreases monotonically with altitude, pressure is continuous
  across layer boundaries, and the geopotential conversion round-trips.
- Reynolds number matches a hand computation (about 6.85e5 for air at sea
  level, 10 m/s, 1 m chord).
- Airspeed conversions round-trip exactly at altitude, EAS equals TAS at
  sea level, and CAS sits above EAS at altitude, as compressibility
  requires.

## Honest limitations

- Standard atmosphere only: no hot, cold, or off-standard days, no
  humidity, no wind or turbulence.
- Altitudes are geopotential and limited to 0 to 51 km, the range the ISA
  layer definitions cover here.
- Airspeed conversions use the subsonic pitot relations. Above Mach 1
  they raise an error instead of returning a wrong number; supersonic
  pitot (Rayleigh) relations are future work.
- Viscosity uses Sutherland's formula with standard air constants; it is
  a model of dry air, not a gas-property database.

These are deliberate. Each one is a clean extension point, listed below.

## Roadmap and room for exploration

Ideas are welcome. Roughly in order of expected value:

- **Off-standard atmospheres**: ISA plus or minus a temperature offset,
  and hot / cold day variants, which is what real performance charts use.
- **Supersonic pitot relations** so CAS conversions cover Mach above 1.
- **Pressure altitude and altimetry helpers**: QNH / QFE conversions,
  flight-level lookup, density altitude.
- **Above 51 km**: extend the layer table into the mesosphere.
- **Unit wrappers**: knots, feet, and inHg convenience conversions for
  cockpit-facing tools, kept out of the SI core.
- **A standard-atmosphere table generator** that emits the classic ISA
  table as CSV or markdown for teaching material.
- **Humidity correction** for virtual temperature and density.

If you build one of these, open an issue or a pull request. Design notes
in the PR description are appreciated: what assumption changed, and what
it did to the validated table values.

## Project structure

```text
src/isa_aero/        the package (atmosphere, aero, cli)
tests/               pytest suite, checked against the published ISA tables
examples/            runnable examples (flight-level table, light aircraft)
.github/workflows/   CI: install and run the test suite on every push
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: fork, branch,
test, pull request. Every change should keep `pytest -q` green and should
not move the validated table values without explaining why in the PR.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Citation

If you use this project in research, please cite the archived release:

Sajid Kabir Saji (2026). isa-aero (v1.0.1) [Software]. Zenodo. https://doi.org/10.5281/zenodo.23077739

The concept DOI https://doi.org/10.5281/zenodo.23077738 always resolves to the latest version.

## License

MIT. See [LICENSE](LICENSE).

## Author

Sajid Kabir Saji, aeronautical engineer. Research interests: onboard
autonomous decision-making for UAVs and solar-electric flight endurance.
More at [sajidkabir.com](https://sajidkabir.com).
