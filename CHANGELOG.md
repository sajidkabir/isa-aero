# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and versions follow
[Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-01

First stable release.

### Added

- Layered ISA atmosphere model from sea level to 51 km covering all five
  standard layers: troposphere, isothermal lower stratosphere, two warming
  stratosphere layers, and the stratopause layer.
- Full state lookup (`state`) returning temperature, pressure, density,
  speed of sound, and dynamic viscosity (Sutherland's formula) at any
  geopotential altitude.
- Geopotential and geometric altitude conversion helpers.
- Aerodynamics helpers: dynamic pressure, Reynolds number, Mach number,
  lift and drag forces from Cl / Cd, and stall speed.
- Airspeed conversions: TAS to EAS by the incompressible density
  correction, and TAS to CAS (and back) through the pitot impact pressure,
  with compressibility accounted for and a clear error above Mach 1.
- Command-line interface with `at` and `convert` subcommands.
- Test suite of 18 tests checked against the published ISA table values at
  sea level, 11 km, and 20 km, plus GitHub Actions CI on Python 3.12.
- Example: ISA flight-level table with a worked light-aircraft stall and
  cruise calculation.
