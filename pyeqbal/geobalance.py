"""
This module contains a set of constant values that are relevent to geographic
balancing of events for a 'clean' amplitude database.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from .constants import GeoBalanceConstants as C


def slices(min: float, max: float, N: float) -> np.ndarray:
    """Convenience function that calls np.linspace and returns
    a numpy array of N linearly spaced values between min, max.

    Args:
        min (float): Minimum value of domain to slice.
        max (float): Maximum value of domain to slice.
        N (float): Number of slices between min and max.

    Returns:
        np.ndarray: An array containing the slices between, and including, min and max.
        
    Raises:
        AssertionError: If the number of slices is < 2, raise an error.
    """
    assert N >= 2, "Need at least two points between start and end. Nmin is 2."

    return np.linspace(min, max, N)


def reduce_event_count_per_voxel(
    df: pd.DataFrame, 
    NOBS_MAX: int = C.NOBS_MAX
    ) -> pd.DataFrame:
    """Convenience function that sorts and then reduces the event count for 
    observations with assigned voxels.

    Args:
        df (pd.DataFrame): A pandas DataFrame that includes the number of 
        observations (num_obs) and assigned voxel numbers.
        EV_MAX (int, optional): [description]. Defaults to C.EV_MAX.

    Returns:
        pd.DataFrame: [description]
    """
    return df.sort_values(["voxel", "num_obs"], ascending=False)\
                           .groupby('voxel')\
                           .head(NOBS_MAX)


def grab_voxel_info(
    voxels: dict,
    X: np.array,
    Y: np.array,
    Z: np.array,
    i: int,
    j: int,
    k: int,
    count: int
    ) -> None:
    """
    Grabs the indexes and creates detailed voxel info which is
    appended to a dictionary for safe keeping.

    Returns None
    """

    voxels['Xrange'].append((X[i], X[i+1]))
    voxels['Yrange'].append((Y[j], Y[j+1]))
    voxels['Zrange'].append((Z[k], Z[k+1]))
    voxels['Xmid'].append(np.median((X[i], X[i+1])))
    voxels['Ymid'].append(np.median((Y[j], Y[j+1])))
    voxels['Zmid'].append(np.median((Z[k], Z[k+1])))
    voxels['Vnum'].append(count)

# TODO: Add function to set slices instead of relying on 'constants.py'.
# TODO: Refactor assign_voxels method for efficiency.
@dataclass()
class Voxels():
    """Voxels dataclass stores information related to voxels for slices in 
    X, Y, Z that are given when an instance of Voxels is created. The default
    values assumed are in the constants.py file, but can be overwritten.

    Returns:
        Voxels: A dataclass with the slices and voxel dataframe.
    """
    x_slices: np.array = slices(C.LON_MIN, C.LON_MAX, C.LON_SLICES),
    y_slices: np.array = slices(C.LAT_MIN, C.LAT_MAX, C.LAT_SLICES),
    z_slices: np.array = slices(C.DEP_MIN, C.DEP_MAX, C.DEP_SLICES)
    
    def __post_init__(self) -> None:
        """Post init to set slices as dict and define a dataframe of voxels.
        """
        self.combine_slices(self.x_slices, self.y_slices, self.z_slices)
 
    def combine_slices(self, x: np.array, y: np.array, z: np.array) -> None:
        """Set all slices in a single dictionary for convenience.

        Args:
            x (np.array): Slices of the x axis.
            y (np.array): Slices of the y axis.
            z (np.array): Slices of the z axis.
        """
        self.all_slices=dict(X=x, Y=y, Z=z)

    def assign_voxels(
        self, 
        df: pd.DataFrame, 
        xlabel: str = C.X_LABEL,
        ylabel: str = C.Y_LABEL,
        zlabel: str = C.Z_LABEL,
        ) -> pd.DataFrame:
        """Iterates over the volumetric pixels (voxels) for the total volume 
        that was segmeneted into smaller volumes according to the slices passed 
        in X, Y, and Z directions. It assigns each voxel a number from 1 to 
        N = X * Y * Z voxels.

        Returns:
            pd.Dataframe: The dataframe with an added column of assigned voxel 
                numbers.
        """

        df = df.copy(deep=True)

        X, Y, Z = self.slices['X'], self.slices['Y'], self.slices['Z']

        cell = []
        bounds = []
        count = 0
        voxel_locs = dict(Xrange=[], Yrange=[], Zrange=[],
                          Xmid=[], Ymid=[], Zmid=[], Vnum=[]
                          )

        # brute force search for events in each sub-volume over entire domain
        # a little slow but can think of ways to optimise later since it works!
        for i in range(len(X[:-1])):
            for j in range(len(Y[:-1])):
                for k in range(len(Z[:-1])):

                    grab_voxel_info(voxel_locs, X, Y, Z, i, j, k, count)
                    cell.append(count)
                    bounds.append(
                                 (df[xlabel]>X[i])&(df[xlabel]<=X[i+1])&\
                                 (df[ylabel]>Y[j])&(df[ylabel]<=Y[j+1])&\
                                 (df[zlabel]>Z[k])&(df[zlabel]<=Z[k+1])
                                  )
                    count += 1
        # assign voxel dataframe back to object for storage
        self.voxels = pd.DataFrame(voxel_locs)
        # create voxel column based on conditions in loop.
        df['voxel'] = np.select(bounds, cell)

        return df
