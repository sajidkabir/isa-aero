"""Aerodynamics helper tests, checked against hand-computed values."""

import pytest

from isa_aero import aero, atmosphere


def test_dynamic_pressure():
    # q = 0.5 * 1.225 * 10^2 = 61.25 Pa.
    assert aero.dynamic_pressure(1.225, 10.0) == pytest.approx(61.25)


def test_reynolds_number_hand_check():
    # Re = rho * V * L / mu = 1.225 * 10 * 1 / 1.789e-5 = about 6.85e5.
    re = aero.reynolds_number(1.225, 10.0, 1.0, 1.789e-5)
    assert re == pytest.approx(684738.0, rel=1e-3)


def test_mach_one_at_sea_level():
    a0 = atmosphere.speed_of_sound(0.0)
    assert a0 == pytest.approx(340.3, abs=0.5)
    assert aero.mach_number(a0, a0) == pytest.approx(1.0)


def test_eas_equals_tas_at_sea_level():
    assert aero.tas_to_eas(80.0, 0.0) == pytest.approx(80.0, rel=1e-3)
    assert aero.eas_to_tas(80.0, 0.0) == pytest.approx(80.0, rel=1e-3)
    assert aero.tas_to_cas(80.0, 0.0) == pytest.approx(80.0, rel=1e-3)


def test_airspeed_round_trips_at_altitude():
    tas = 200.0
    h = 8000.0
    assert aero.eas_to_tas(aero.tas_to_eas(tas, h), h) == pytest.approx(tas, rel=1e-9)
    assert aero.cas_to_tas(aero.tas_to_cas(tas, h), h) == pytest.approx(tas, rel=1e-9)


def test_cas_above_eas_at_altitude():
    # At altitude the pitot senses compressibility, so CAS sits above EAS
    # for the same TAS, and both sit below TAS.
    tas, h = 200.0, 8000.0
    eas = aero.tas_to_eas(tas, h)
    cas = aero.tas_to_cas(tas, h)
    assert eas < cas < tas


def test_lift_drag_and_stall_speed():
    # L = q * S * Cl = 61.25 * 2 * 1.0 = 122.5 N at sea level, 10 m/s.
    assert aero.lift_force(1.0, 1.225, 10.0, 2.0) == pytest.approx(122.5)
    assert aero.drag_force(0.05, 1.225, 10.0, 2.0) == pytest.approx(6.125)
    # 100 kg aircraft, 10 m2 wing, Cl_max 1.5: Vs = about 10.33 m/s at sea level.
    vs = aero.stall_speed(100.0, 10.0, 1.5)
    assert vs == pytest.approx(10.33, abs=0.02)
    # Thinner air at altitude means a higher true stall speed.
    assert aero.stall_speed(100.0, 10.0, 1.5, altitude_m=5000.0) > vs


def test_supersonic_cas_conversion_raises():
    with pytest.raises(ValueError):
        aero.tas_to_cas(400.0, 0.0)
