"""
This module contains a set of constant values that are relevent to formatting
and cleaning the database.
"""
from dataclasses import dataclass

@dataclass(init=False)
class GeoBalanceConstants():
    """Constants for balancing the spatial distribution of earthquakes.
    """
    X_LABEL: str = "EqLon"
    Y_LABEL: str = "EqLat"
    Z_LABEL: str = "EqDep"
    X_MIN: float = -113.5
    X_MAX: float = -109
    Y_MIN: float = 43.7
    Y_MAX: float = 45.7
    Z_MIN: float = 0
    Z_MAX: float = 25
    X_SLICES: int = 35
    Y_SLICES: int = 35
    Z_SLICES: int = 6
    NOBS_MAX: int = 10