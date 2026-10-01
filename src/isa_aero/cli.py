"""Command-line interface for isa-aero.

Usage:
    isa-aero at --altitude 11000
    isa-aero convert --tas 250 --altitude 11000
"""

from __future__ import annotations

import argparse

from . import aero, atmosphere


def _cmd_at(args: argparse.Namespace) -> int:
    s = atmosphere.state(args.altitude)
    print(f"ISA state at {args.altitude:.0f} m (geopotential)")
    print(f"  Temperature:     {s.temperature_k:.2f} K ({s.temperature_c:.2f} C)")
    print(f"  Pressure:        {s.pressure_pa:.1f} Pa")
    print(f"  Density:         {s.density_kg_m3:.4f} kg/m3")
    print(f"  Speed of sound:  {s.speed_of_sound_m_s:.2f} m/s")
    print(f"  Viscosity:       {s.dynamic_viscosity_pa_s:.4e} Pa s")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    tas = args.tas
    a = atmosphere.speed_of_sound(args.altitude)
    eas = aero.tas_to_eas(tas, args.altitude)
    cas = aero.tas_to_cas(tas, args.altitude)
    print(f"Airspeed conversion at {args.altitude:.0f} m (ISA)")
    print(f"  TAS:             {tas:.2f} m/s (Mach {aero.mach_number(tas, a):.3f})")
    print(f"  EAS:             {eas:.2f} m/s")
    print(f"  CAS:             {cas:.2f} m/s")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="isa-aero",
        description="ISA atmosphere and aerodynamics utilities.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_at = sub.add_parser("at", help="print the full ISA state at an altitude")
    p_at.add_argument(
        "--altitude", type=float, default=0.0,
        help="geopotential altitude in metres (default 0)",
    )
    p_at.set_defaults(func=_cmd_at)

    p_conv = sub.add_parser(
        "convert", help="convert a true airspeed to EAS and CAS at an altitude"
    )
    p_conv.add_argument(
        "--tas", type=float, default=100.0,
        help="true airspeed in m/s (default 100)",
    )
    p_conv.add_argument(
        "--altitude", type=float, default=0.0,
        help="geopotential altitude in metres (default 0)",
    )
    p_conv.set_defaults(func=_cmd_convert)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
