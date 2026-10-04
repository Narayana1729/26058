"""
tgc_generator.py
================
Single responsibility: compute propagation-loss-derived TGC tables.

The physics is:
    TL_2way(R, f) = 40*log10(R) + 2*alpha(f)*R     [dB]

where alpha(f) is the ONE-WAY absorption coefficient from acoustic_model.py.
The factor of 2 for two-way propagation is applied HERE, not in alpha_dB_per_m().

Output is gain in dB. Hardware conversion (dB → DAC code) is a separate step.
This prevents the physics model from being coupled to a specific AFE.

Design rules
------------
- alpha_fn is an injected callable: alpha_fn(f_hz) -> float [dB/m, one-way]
- R=0 is handled by R_MIN clamping. log10(0) is never evaluated.
- TGC dB values are clipped to hardware limits BEFORE DAC conversion.
- Theoretical (unclipped) values are also returned for analysis.
- No side effects. No file I/O. No plotting.
"""

import math
import numpy as np
from typing import Callable, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
R_MIN: float = 0.05    # [m] minimum range — log10(R) clamp, not physical claim

# Hardware gain limits — AD8331 / AD603 VGA dynamic range
MIN_TGC_DB: float = 0.0    # [dB]
MAX_TGC_DB: float = 40.0   # [dB] — nominal 40 dB linear-in-dB gain control range

DAC_BITS: int = 12
DAC_MAX_CODE: int = (1 << DAC_BITS) - 1   # 4095


# ---------------------------------------------------------------------------
# Core propagation loss
# ---------------------------------------------------------------------------
def tl_2way_dB(R: float, alpha_one_way_dB_per_m: float) -> float:
    """
    Two-way transmission loss [dB] for a monostatic point target.

    TL = 40*log10(R) + 2*alpha*R

    Parameters
    ----------
    R                      : range [m], must be > 0
    alpha_one_way_dB_per_m : one-way absorption [dB/m] from acoustic_model.py

    Returns
    -------
    float : TL [dB]

    Raises
    ------
    ValueError if R <= 0.
    """
    if R <= 0.0:
        raise ValueError(f"Range R must be > 0, got {R}")
    return 40.0 * math.log10(R) + 2.0 * alpha_one_way_dB_per_m * R


# ---------------------------------------------------------------------------
# Range array
# ---------------------------------------------------------------------------
def sample_to_range(sample_index: np.ndarray,
                    Fs: float,
                    c: float) -> np.ndarray:
    """
    Convert sample indices to one-way range.

    R = c * (sample_index / Fs) / 2

    Clamps to R_MIN to avoid log10(0).

    Parameters
    ----------
    sample_index : array of sample indices (0-based)
    Fs           : sampling rate [Hz]
    c            : sound speed [m/s]

    Returns
    -------
    np.ndarray : range [m], clipped to >= R_MIN
    """
    R = c * (sample_index.astype(float) / Fs) / 2.0
    return np.maximum(R, R_MIN)


# ---------------------------------------------------------------------------
# TGC table generators
# ---------------------------------------------------------------------------
def generate_tgc_db(alpha_fn: Callable[[float], float],
                    f_hz: float,
                    n_samples: int,
                    Fs: float,
                    c: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate TGC gain profile for one frequency/mode.

    Returns theoretical (unclipped), clipped, and range arrays.

    Parameters
    ----------
    alpha_fn  : callable alpha_fn(f_hz) -> float [dB/m, one-way]
    f_hz      : carrier frequency [Hz]
    n_samples : number of samples in LUT
    Fs        : sampling rate [Hz]
    c         : sound speed [m/s]

    Returns
    -------
    ranges_m      : np.ndarray [m]
    tgc_db_theory : np.ndarray [dB] — unclipped theoretical TL
    tgc_db_clipped: np.ndarray [dB] — clipped to [MIN_TGC_DB, MAX_TGC_DB]
    """
    alpha = alpha_fn(f_hz)   # one-way, dB/m
    sample_idx = np.arange(1, n_samples + 1)  # 1-indexed: sample 0 → R=0 is avoided
    ranges_m = sample_to_range(sample_idx, Fs, c)

    tgc_db_theory = 40.0 * np.log10(ranges_m) + 2.0 * alpha * ranges_m
    tgc_db_clipped = np.clip(tgc_db_theory, MIN_TGC_DB, MAX_TGC_DB)

    return ranges_m, tgc_db_theory, tgc_db_clipped


def dac_code_from_gain_db(gain_db: np.ndarray,
                           min_db: float = MIN_TGC_DB,
                           max_db: float = MAX_TGC_DB,
                           dac_bits: int = DAC_BITS) -> np.ndarray:
    """
    Convert gain [dB] to unsigned DAC codes.

    Linear mapping: min_db -> 0,  max_db -> (2^dac_bits - 1)

    This function is the ONLY place that knows about DAC resolution.
    Swap this function if the hardware AFE changes.

    Parameters
    ----------
    gain_db  : clipped gain array [dB]
    min_db   : gain at DAC code 0
    max_db   : gain at DAC code max
    dac_bits : DAC resolution in bits

    Returns
    -------
    np.ndarray : uint16 DAC codes
    """
    dac_max = (1 << dac_bits) - 1
    scale = dac_max / (max_db - min_db) if (max_db - min_db) > 0 else 0.0
    codes = np.round((gain_db - min_db) * scale).astype(int)
    return np.clip(codes, 0, dac_max).astype(np.uint16)
