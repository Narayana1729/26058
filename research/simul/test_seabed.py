"""Unit tests for seabed_model.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from seabed_model import (acoustic_impedance, reflection_coeff, bottom_loss_dB,
                          theoretical_bl_table, classify_nearest_reference,
                          SeabedType, WATER_REF)

def test_water_impedance():
    rho, c = WATER_REF
    Z = acoustic_impedance(rho, c)
    assert abs(Z - rho*c) < 1e-6

def test_reflection_coeff_identical_media():
    """Same media -> Rp = 0."""
    Z = 1_537_500.0
    assert reflection_coeff(Z, Z) == 0.0

def test_reflection_coeff_rock_positive():
    """Rock Z > Water Z -> Rp > 0."""
    Z_water = acoustic_impedance(*WATER_REF)
    Z_rock  = acoustic_impedance(2700, 3500)
    assert reflection_coeff(Z_water, Z_rock) > 0

def test_bl_increases_for_softer_material():
    """Softer material -> higher BL (weaker echo)."""
    tbl = theoretical_bl_table()
    assert tbl["Soft Mud"].BL_dB > tbl["Sand"].BL_dB
    assert tbl["Sand"].BL_dB > tbl["Limestone/Rock"].BL_dB

def test_bl_rock_low():
    """Rock BL should be low (strong reflection)."""
    tbl = theoretical_bl_table()
    assert tbl["Limestone/Rock"].BL_dB < 5.0

def test_classify_exact_rock():
    """Perfect rock BL -> classify as ROCK."""
    tbl = theoretical_bl_table()
    bl_rock = tbl["Limestone/Rock"].BL_dB
    result = classify_nearest_reference(bl_rock)
    assert result.candidate == SeabedType.ROCK

def test_classify_unknown_on_bad_input():
    result = classify_nearest_reference(float('nan'))
    assert result.candidate == SeabedType.UNKNOWN

def test_all_materials_in_table():
    tbl = theoretical_bl_table()
    for name in ["Soft Mud", "Sandy Mud", "Sand", "Gravel", "Limestone/Rock"]:
        assert name in tbl, f"Missing: {name}"

if __name__ == "__main__":
    tests = [k for k in dir() if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            eval(f"{t}()")
            print(f"  PASS  {t}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
