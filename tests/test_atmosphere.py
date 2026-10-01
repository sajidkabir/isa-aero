"""ISA atmosphere tests, checked against the published standard tables."""

import pytest

from isa_aero import atmosphere


def test_sea_level_standard_values():
    assert atmosphere.temperature(0.0) == pytest.approx(288.15)
    assert atmosphere.pressure(0.0) == pytest.approx(101325.0)
    assert atmosphere.density(0.0) == pytest.approx(1.225, rel=1e-3)
    # Speed of sound at sea level: about 340.3 m/s.
    assert atmosphere.speed_of_sound(0.0) == pytest.approx(340.3, abs=0.5)
    # Dynamic viscosity at sea level: about 1.789e-5 Pa s.
    assert atmosphere.dynamic_viscosity(0.0) == pytest.approx(1.789e-5, rel=1e-2)


def test_tropopause_11km_values():
    # Published ISA table values at 11 km.
    assert atmosphere.temperature(11000.0) == pytest.approx(216.65)
    assert atmosphere.pressure(11000.0) == pytest.approx(22632.06, rel=2e-3)
    assert atmosphere.density(11000.0) == pytest.approx(0.36392, rel=2e-3)


def test_stratosphere_20km_values():
    # Published ISA table values at 20 km.
    assert atmosphere.temperature(20000.0) == pytest.approx(216.65)
    assert atmosphere.pressure(20000.0) == pytest.approx(5474.89, rel=2e-3)
    assert atmosphere.density(20000.0) == pytest.approx(0.08802, rel=2e-3)


def test_32km_temperature():
    # 216.65 K at 20 km plus a +1.0 K/km lapse over 12 km gives 228.65 K.
    assert atmosphere.temperature(32000.0) == pytest.approx(228.65, abs=0.01)


def test_troposphere_lapse_rate():
    drop_per_km = (atmosphere.temperature(0.0) - atmosphere.temperature(10000.0)) / 10.0
    assert drop_per_km == pytest.approx(6.5, abs=1e-9)


def test_isothermal_lower_stratosphere():
    assert atmosphere.temperature(11000.0) == pytest.approx(216.65)
    assert atmosphere.temperature(15000.0) == pytest.approx(216.65)
    assert atmosphere.temperature(20000.0) == pytest.approx(216.65)


def test_density_decreases_monotonically():
    altitudes = [500.0 * i for i in range(41)]  # 0 to 20,000 m
    densities = [atmosphere.density(h) for h in altitudes]
    assert all(b < a for a, b in zip(densities, densities[1:]))


def test_geopotential_round_trip():
    geo = atmosphere.geometric_to_geopotential(11000.0)
    # Geometric 11,000 m is about 10,981 m geopotential.
    assert geo == pytest.approx(10981.0, abs=1.0)
    assert atmosphere.geopotential_to_geometric(geo) == pytest.approx(11000.0, rel=1e-9)


def test_pressure_continuous_at_layer_boundary():
    below = atmosphere.pressure(19999.9)
    above = atmosphere.pressure(20000.1)
    assert above == pytest.approx(below, rel=1e-4)


def test_altitude_out_of_range_raises():
    with pytest.raises(ValueError):
        atmosphere.temperature(60000.0)
    with pytest.raises(ValueError):
        atmosphere.pressure(-100.0)
