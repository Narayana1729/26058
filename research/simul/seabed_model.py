"""
seabed_model.py
===============
Single responsibility: acoustic impedance and seabed reflection physics.

All values are idealised reference calculations for normal-incidence,
homogeneous half-space interfaces.

DISCLAIMER (embed in any output that references classification):
    Coarse reference classification under controlled experimental conditions.
    Real seabed classification also depends on grazing angle, roughness,
    sediment layering, frequency, grain size, porosity, and transducer directivity.

Design rules
------------
- No side effects. No file I/O. No plotting.
- Classification returns SEABED_UNKNOWN when BL is outside all reference ranges.
- Use nearest-reference classification: argmin |BL_measured - BL_i|.
"""

import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Material table — idealised reference values
# (rho [kg/m³], c [m/s])
# ---------------------------------------------------------------------------
WATER_REF: Tuple[float, float] = (1025.0, 1500.0)

MATERIAL_TABLE: Dict[str, Tuple[float, float]] = {
    "Soft Mud":       (1150.0, 1480.0),
    "Sandy Mud":      (1600.0, 1600.0),
    "Sand":           (1900.0, 1700.0),
    "Gravel":         (2000.0, 1800.0),
    "Limestone/Rock": (2700.0, 3500.0),
}

SEABED_DISCLAIMER: str = (
    "Coarse reference classification under controlled experimental conditions. "
    "Real seabed classification also depends on grazing angle, roughness, "
    "sediment layering, frequency, grain size, porosity, density, sound speed "
    "gradient, volume scattering, and transducer directivity."
)


# ---------------------------------------------------------------------------
# SeabedType enum
# ---------------------------------------------------------------------------
class SeabedType(IntEnum):
    UNKNOWN    = 0
    SOFT_MUD   = 1
    SANDY_MUD  = 2
    SAND       = 3
    GRAVEL     = 4
    ROCK       = 5


_MATERIAL_TO_TYPE: Dict[str, SeabedType] = {
    "Soft Mud":       SeabedType.SOFT_MUD,
    "Sandy Mud":      SeabedType.SANDY_MUD,
    "Sand":           SeabedType.SAND,
    "Gravel":         SeabedType.GRAVEL,
    "Limestone/Rock": SeabedType.ROCK,
}


# ---------------------------------------------------------------------------
# Pure physics functions
# ---------------------------------------------------------------------------
def acoustic_impedance(rho: float, c: float) -> float:
    """Z = rho * c  [Rayl = Pa·s/m]."""
    return rho * c


def reflection_coeff(Z1: float, Z2: float) -> float:
    """
    Normal-incidence pressure reflection coefficient.
    Rp = (Z2 - Z1) / (Z2 + Z1)
    Returns signed value in [-1, 1].
    """
    return (Z2 - Z1) / (Z2 + Z1)


def bottom_loss_dB(Rp: float) -> float:
    """
    BL = -20 * log10(|Rp|)  [dB]
    Higher BL = weaker echo (soft sediment, small impedance contrast).
    Lower BL  = stronger echo (hard rock, large impedance contrast).
    Returns float('inf') if Rp == 0.
    """
    abs_rp = abs(Rp)
    if abs_rp < 1.0e-12:
        return float('inf')
    return -20.0 * math.log10(abs_rp)


# ---------------------------------------------------------------------------
# Reference table
# ---------------------------------------------------------------------------
@dataclass
class SeabedReference:
    name:    str
    rho:     float    # kg/m³
    c:       float    # m/s
    Z:       float    # Rayl
    Rp:      float    # dimensionless
    BL_dB:   float    # dB
    stype:   SeabedType


def theoretical_bl_table() -> Dict[str, SeabedReference]:
    """
    Returns BL for each material in MATERIAL_TABLE vs WATER_REF.
    Result is a dict keyed by material name.
    """
    rho_w, c_w = WATER_REF
    Z_water = acoustic_impedance(rho_w, c_w)
    table = {}
    for name, (rho, c) in MATERIAL_TABLE.items():
        Z2 = acoustic_impedance(rho, c)
        Rp = reflection_coeff(Z_water, Z2)
        BL = bottom_loss_dB(Rp)
        table[name] = SeabedReference(
            name=name, rho=rho, c=c, Z=Z2, Rp=Rp, BL_dB=BL,
            stype=_MATERIAL_TO_TYPE[name]
        )
    return table


# ---------------------------------------------------------------------------
# Nearest-reference classifier
# ---------------------------------------------------------------------------
@dataclass
class ClassificationResult:
    candidate:    SeabedType
    candidate_name: str
    bl_measured:  float   # dB  (input)
    bl_reference: float   # dB  (nearest reference)
    bl_error_dB:  float   # bl_measured - bl_reference
    note:         str     = SEABED_DISCLAIMER


def classify_nearest_reference(bl_measured_dB: float,
                                max_error_dB: float = 15.0) -> ClassificationResult:
    """
    Coarse substrate classification by nearest-reference BL.

    Algorithm: argmin_i |BL_measured - BL_ref_i|

    Returns UNKNOWN if best match error exceeds max_error_dB, or if
    bl_measured is non-finite.

    Parameters
    ----------
    bl_measured_dB : measured bottom loss [dB] (after propagation correction)
    max_error_dB   : maximum acceptable classification error [dB]

    Returns
    -------
    ClassificationResult
    """
    if not math.isfinite(bl_measured_dB):
        return ClassificationResult(
            candidate=SeabedType.UNKNOWN,
            candidate_name="Unknown",
            bl_measured=bl_measured_dB,
            bl_reference=float('nan'),
            bl_error_dB=float('nan'),
        )

    ref_table = theoretical_bl_table()
    best_name = None
    best_err  = float('inf')

    for name, ref in ref_table.items():
        err = abs(bl_measured_dB - ref.BL_dB)
        if err < best_err:
            best_err  = err
            best_name = name

    if best_err > max_error_dB:
        return ClassificationResult(
            candidate=SeabedType.UNKNOWN,
            candidate_name="Unknown (error too large)",
            bl_measured=bl_measured_dB,
            bl_reference=ref_table[best_name].BL_dB,
            bl_error_dB=bl_measured_dB - ref_table[best_name].BL_dB,
        )

    ref = ref_table[best_name]
    return ClassificationResult(
        candidate=ref.stype,
        candidate_name=best_name,
        bl_measured=bl_measured_dB,
        bl_reference=ref.BL_dB,
        bl_error_dB=bl_measured_dB - ref.BL_dB,
    )
