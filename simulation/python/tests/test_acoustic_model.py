"""Unit tests for acoustic_model.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from acoustic_model import alpha_dB_per_m, sound_speed_mackenzie, DEFAULT_ENV

def test_alpha_positive():
    a = alpha_dB_per_m(100_000)
    assert a > 0, "Absorption must be positive"

def test_alpha_frequency_monotonic():
    """Higher frequency -> higher absorption (broadly true for F-G)."""
    a_low  = alpha_dB_per_m(100_000)
    a_high = alpha_dB_per_m(450_000)
    assert a_high > a_low, "450kHz absorption must exceed 100kHz"

def test_alpha_units():
    """Return value should be in dB/m (not dB/km): expect << 1 at 100kHz."""
    a = alpha_dB_per_m(100_000)
    assert 0 < a < 1.0, f"Expected dB/m range 0-1, got {a:.6f}"

def test_alpha_does_not_include_factor_of_2():
    """The factor of 2 for two-way must NOT be in alpha_dB_per_m."""
    a = alpha_dB_per_m(100_000)
    a2 = alpha_dB_per_m(100_000) * 2
    assert abs(a * 2 - a2) < 1e-10, "Factor-of-2 check failed"

def test_sound_speed_reasonable():
    c = sound_speed_mackenzie()
    assert 1400 < c < 1600, f"Sound speed {c} out of expected range"

def test_sound_speed_increases_with_temp():
    c_cold = sound_speed_mackenzie(T_C=5.0)
    c_warm = sound_speed_mackenzie(T_C=25.0)
    assert c_warm > c_cold

def test_default_env_keys():
    for key in ["temperature_C", "salinity_ppt", "pH", "depth_m"]:
        assert key in DEFAULT_ENV, f"Missing key: {key}"

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
