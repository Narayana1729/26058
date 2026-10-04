"""
acoustic_model.py
=================
Single responsibility: seawater acoustic physics.

Functions
---------
alpha_dB_per_m(f_hz, T_C, S_ppt, D_m, pH) -> float
    One-way absorption coefficient [dB/m].
    Source: Francois & Garrison, JASA 72(3), 1982.
    Valid: 400 Hz – 1 MHz.

sound_speed_mackenzie(T_C, S_ppt, D_m) -> float
    Sound speed [m/s].
    Source: Mackenzie, JASA 70(3), 1981.

Constants
---------
DEFAULT_ENV : dict
    Simulation reference environment.
    Label: initial simulation defaults, NOT claims about actual ocean.

Design rules
------------
- No side effects. No file I/O. No plotting.
- All quantities in SI units unless the name says otherwise.
- The factor of 2 for two-way absorption is NOT applied here.
  Apply it in tgc_generator.py.
"""

# ---------------------------------------------------------------------------
# Default environment — simulation reference only
# ---------------------------------------------------------------------------
DEFAULT_ENV = {
    "temperature_C": 20.0,  # °C
    "salinity_ppt":  35.0,  # parts per thousand
    "pH":             8.0,
    "depth_m":       10.0,  # m
}


def alpha_dB_per_m(f_hz: float,
                   T_C:    float = None,
                   S_ppt:  float = None,
                   D_m:    float = None,
                   pH:     float = None,
                   **kwargs) -> float:
    """
    One-way seawater absorption coefficient [dB/m].

    Uses Francois-Garrison (1982) three-term relaxation model:
        alpha = alpha_boric + alpha_MgSO4 + alpha_water

    Parameters
    ----------
    f_hz   : acoustic frequency [Hz]
    T_C    : temperature [°C] (or temperature_C in kwargs)
    S_ppt  : salinity [ppt] (or salinity_ppt in kwargs)
    D_m    : depth [m] (or depth_m in kwargs)
    pH     : seawater pH

    Returns
    -------
    float : one-way absorption coefficient [dB/m]
    """
    import math

    # Handle aliases or defaults
    if T_C is None:
        T_C = kwargs.get("temperature_C", DEFAULT_ENV["temperature_C"])
    if S_ppt is None:
        S_ppt = kwargs.get("salinity_ppt", DEFAULT_ENV["salinity_ppt"])
    if D_m is None:
        D_m = kwargs.get("depth_m", DEFAULT_ENV["depth_m"])
    if pH is None:
        pH = kwargs.get("pH", DEFAULT_ENV["pH"])

    f_kHz = f_hz / 1.0e3

    # --- Term 1: Boric acid (B(OH)3) ---
    # Coefficients in F-G (1982) internal units.
    A1 = 8.86 / 1.0e3 * 10.0 ** (0.78 * pH - 5.0)
    f1 = 2.8 * math.sqrt(S_ppt / 35.0) * 10.0 ** (4.0 - 1245.0 / (T_C + 273.0))
    alpha_boric = A1 * f1 * f_kHz ** 2 / (f1 ** 2 + f_kHz ** 2)

    # --- Term 2: MgSO4 ---
    A2 = 21.44 * S_ppt * (1.0 + 0.025 * T_C)   # internal units (NOT pre-divided)
    f2 = (8.17 * 10.0 ** (8.0 - 1990.0 / (T_C + 273.0))) / (1.0 + 0.0018 * (S_ppt - 35.0))
    P2 = 1.0 - 1.37e-4 * D_m + 6.2e-9 * D_m ** 2
    alpha_mgso4 = (A2 / 1.0e3) * P2 * f2 * f_kHz ** 2 / (f2 ** 2 + f_kHz ** 2)

    # --- Term 3: Pure water viscosity ---
    if T_C <= 20.0:
        A3 = 4.937e-4 - 2.59e-5 * T_C + 9.11e-7 * T_C ** 2 - 1.50e-8 * T_C ** 3
    else:
        A3 = 3.964e-4 - 1.146e-5 * T_C + 1.45e-7 * T_C ** 2 - 6.5e-10 * T_C ** 3
    P3 = 1.0 - 3.83e-5 * D_m + 4.9e-10 * D_m ** 2
    alpha_water = A3 * P3 * f_kHz ** 2

    # All three terms are now in the same F-G internal unit system.
    # Sum and divide by 1000 to convert to dB/m (one-way).
    # The factor of 2 for two-way propagation is applied in tgc_generator.py,
    # NOT here. Keep this function's output strictly one-way dB/m.
    alpha_sum_internal = alpha_boric + alpha_mgso4 + alpha_water
    return alpha_sum_internal / 1000.0   # dB/m, one-way


def sound_speed_mackenzie(T_C:   float = None,
                          S_ppt: float = None,
                          D_m:   float = None,
                          **kwargs) -> float:
    """
    Sound speed in seawater [m/s].

    Uses Mackenzie (1981) nine-term equation.
    Valid: T 2–30 °C, S 25–40 ppt, D 0–8000 m.

    Parameters
    ----------
    T_C   : temperature [°C] (or temperature_C in kwargs)
    S_ppt : salinity [ppt] (or salinity_ppt in kwargs)
    D_m   : depth [m] (or depth_m in kwargs)

    Returns
    -------
    float : sound speed [m/s]
    """
    if T_C is None:
        T_C = kwargs.get("temperature_C", DEFAULT_ENV["temperature_C"])
    if S_ppt is None:
        S_ppt = kwargs.get("salinity_ppt", DEFAULT_ENV["salinity_ppt"])
    if D_m is None:
        D_m = kwargs.get("depth_m", DEFAULT_ENV["depth_m"])

    c = (1448.96
         + 4.591  * T_C
         - 5.304e-2 * T_C ** 2
         + 2.374e-4 * T_C ** 3
         + 1.340  * (S_ppt - 35.0)
         + 1.630e-2 * D_m
         + 1.675e-7 * D_m ** 2
         - 1.025e-2 * T_C * (S_ppt - 35.0)
         - 7.139e-13 * T_C * D_m ** 3)
    return c
