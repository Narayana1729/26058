"""Unit tests for tgc_generator.py"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Simul", "python"))
from acoustic_model import alpha_dB_per_m
from tgc_generator  import (tl_2way_dB, sample_to_range, generate_tgc_db,
                             dac_code_from_gain_db, R_MIN, MIN_TGC_DB, MAX_TGC_DB, DAC_BITS)

def test_tl_2way_uses_two_alpha():
    """TL_2way must use 2*alpha*R, not alpha*R."""
    alpha = alpha_dB_per_m(100_000)
    R = 1.0
    tl = tl_2way_dB(R, alpha)
    spreading = 40 * np.log10(R)
    absorption_2way = 2 * alpha * R
    assert abs(tl - spreading - absorption_2way) < 1e-10

def test_tl_2way_raises_on_zero():
    raised = False
    try:
        tl_2way_dB(0.0, 0.05)
    except ValueError:
        raised = True
    assert raised, "Should have raised ValueError on R <= 0"

def test_r_min_clamping():
    """sample 0 should map to R_MIN, not 0."""
    idx = np.array([0, 1, 2])
    R = sample_to_range(idx, 100_000.0, 1500.0)
    assert all(R >= R_MIN)

def test_clipped_does_not_exceed_max():
    alpha = lambda f: alpha_dB_per_m(f)
    _, theory, clipped = generate_tgc_db(alpha, 450_000, 512, 100_000.0, 1500.0)
    assert np.all(clipped <= MAX_TGC_DB + 1e-6)
    assert np.all(clipped >= MIN_TGC_DB - 1e-6)

def test_dac_codes_in_range():
    gain = np.linspace(MIN_TGC_DB, MAX_TGC_DB, 100)
    codes = dac_code_from_gain_db(gain)
    assert np.all(codes >= 0)
    assert np.all(codes <= (1 << DAC_BITS) - 1)

def test_dac_code_min_max():
    codes_min = dac_code_from_gain_db(np.array([MIN_TGC_DB]))
    codes_max = dac_code_from_gain_db(np.array([MAX_TGC_DB]))
    assert codes_min[0] == 0
    assert codes_max[0] == (1 << DAC_BITS) - 1

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
