import math
from solution import to_celsius


def test_water_freezes_at_zero_celsius():
    assert math.isclose(to_celsius(32), 0.0, abs_tol=1e-9)


def test_water_boils_at_one_hundred_celsius():
    assert math.isclose(to_celsius(212), 100.0, abs_tol=1e-9)


def test_negative_temperature():
    assert math.isclose(to_celsius(-40), -40.0, abs_tol=1e-9)
