"""Print the ISA state in 2 km steps and work one light-aircraft example.

Run from the repo root after `pip install -e .`:
    python examples/flight_levels.py
"""

from isa_aero import aero, atmosphere


def main() -> None:
    print("ISA atmosphere, sea level to 12 km")
    print(f"{'Alt (m)':>8} {'T (K)':>8} {'P (Pa)':>10} {'rho':>7} {'a (m/s)':>8}")
    for h in range(0, 12001, 2000):
        s = atmosphere.state(float(h))
        print(
            f"{h:>8} {s.temperature_k:>8.2f} {s.pressure_pa:>10.1f} "
            f"{s.density_kg_m3:>7.4f} {s.speed_of_sound_m_s:>8.2f}"
        )

    # A 600 kg light aircraft with an 11 m2 wing and Cl_max 1.6.
    print()
    print("Light aircraft, 600 kg, 11 m2 wing, Cl_max 1.6")
    for h in (0.0, 3000.0):
        vs = aero.stall_speed(600.0, 11.0, 1.6, altitude_m=h)
        print(f"  Stall speed at {h:.0f} m: {vs:.1f} m/s TAS")
    tas = 55.0
    h = 3000.0
    rho = atmosphere.density(h)
    mu = atmosphere.dynamic_viscosity(h)
    re = aero.reynolds_number(rho, tas, 1.5, mu)
    print(f"  Cruising at {tas:.0f} m/s TAS at {h:.0f} m:")
    print(f"    EAS {aero.tas_to_eas(tas, h):.1f} m/s, CAS {aero.tas_to_cas(tas, h):.1f} m/s")
    print(f"    Reynolds number on a 1.5 m chord: {re:.3e}")


if __name__ == "__main__":
    main()
