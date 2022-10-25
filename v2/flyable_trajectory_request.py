# -*- coding: utf-8 -*-
"""
Flyable trajectory request schema
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FlyableTrajectoryRequest(CallbackRequest):
    """
    Flyable trajectory request in accordance with
    the NASA DRF Trajectory Service Specification
    \f

    Parameters
    ----------
        BaseModel : pydantic.ModelMetaclass

    Attributes
    ----------
        status              : int, optional
                              status
        tsim_datetime       : list, optional
                              trajectory datetime values
        ref_datetime        : datetime, optional
                              reference datetime for the relative trajectory time
        tsim_s              : list
                              relative trajectory time in seconds
        latitude_deg        : list
                              latitude in degrees
        longitude_deg       : list
                              longitude in degrees
        h_ft                : list
                              relative height above ground in ft
        xe_ft               : list, optional
                              relative x-cartesian coordinate, ft in earth frame
        ye_ft               : list, optional
                              relative y-cartesian coordinate, ft in earth frame
        psi_deg             : list, optional
                              heading in degrees
        airspepd_ktas       : list, optional
                              true airspeed in knots
        Omega_radps         : list, optional
                              rotor rates rad/s, one row per motor
        env_V               : list, optional
                              engine voltage input, one row per motor
        env_I_A             : list, optional
                              engine current input in Amps, one row per motor
        env_Q_ftlbs         : list, optional
                              engine torque in ft-lbs, one row per motor
        maxdev_radius_ft    : list, optional
                              maximum radial deviation in ft
        maxdev_height_ft    : list, optional
                              maximum height deviation in ft
        maxdev_heading_deg  : list, optional
                              maximum heading deviation in degrees

    Raises
    -------
        ValidationError
            if the input data cannot be parsed to form a valid model

    Returns
    -------
        object
                :class:`FlyableTrajectoryRequest` created object

    """

    status: Optional[int] = Field(None, title="status")
    tsim_datetime: Optional[List[datetime]] = Field([], title="trajectory datetime")
    ref_datetime: Optional[datetime] = Field(
        None, title="reference datetime for the relative trajectory"
    )
    tsim_s: List[float] = Field([], title="relative trajectory time in seconds")
    latitude_deg: List[float] = Field([], title="latitude in degrees")
    longitude_deg: List[float] = Field([], title="longitude in degrees")
    h_ft: List[float] = Field([], title="relative height above ground in ft")
    xe_ft: Optional[List[float]] = Field(
        None, title="relative x-cartesian coordinate, ft in earth frame"
    )
    ye_ft: Optional[List[float]] = Field(
        None, title="relative y-cartesian coordinate, ft in earth frame"
    )
    psi_deg: Optional[List[float]] = Field(None, title="heading in degrees")
    airspepd_ktas: Optional[List[float]] = Field(None, title="airspeed in knots")
    Omega_radps: Optional[List[List[float]]] = Field(
        None, title="rotor rates rad/s, one row per motor"
    )
    env_V: Optional[List[List[float]]] = Field(
        None, title="engine voltage input, one row per motor"
    )
    env_I_A: Optional[List[List[float]]] = Field(
        None, title="engine current input in Amps, one row per motor"
    )
    env_Q_ftlbs: Optional[List[List[float]]] = Field(
        None, title="engine torque in ft-lbs, one row per motor"
    )
    maxdev_radius_ft: Optional[List[float]] = Field(
        None, title="maximum radial deviation in ft"
    )
    maxdev_height_ft: Optional[List[float]] = Field(
        None, title="maximum height deviation in ft"
    )
    maxdev_heading_deg: Optional[List[float]] = Field(
        None, title="maximum heading deviation in degrees"
    )

    class Config:
        schema_extra = {
            "example": {
                "tsim_datetime": [
                    "2022-08-30 16:20:32",
                    "2022-08-30 16:30:16",
                    "2022-08-30 16:45:29",
                    "2022-08-30 16:50:23",
                    "2022-08-30 17:00:15",
                    "2022-08-30 17:10:30",
                    "2022-08-30 17:17:32",
                    "2022-08-30 17:25:02",
                    "2022-08-30 17:30:11",
                    "2022-08-30 17:40:26",
                    "2022-08-30 17:45:27",
                    "2022-08-30 18:00:00",
                    "2022-08-30 18:10:01",
                    "2022-08-30 18:18:00",
                    "2022-08-30 18:22:29",
                    "2022-08-30 18:26:05",
                    "2022-08-30 18:30:09",
                    "2022-08-30 18:33:12",
                    "2022-08-30 19:10:01",
                    "2022-08-30 19:40:33",
                ],
                "latitude_deg": [
                    33.65226900226935,
                    33.623018821849,
                    33.569654688600444,
                    33.466275533321145,
                    33.473171319752915,
                    33.45248231452024,
                    33.364934792297014,
                    33.33921415314476,
                    33.33186400341638,
                    33.295103953469166,
                    33.293265544133725,
                    33.28039559416502,
                    33.27120161080551,
                    33.23076936044074,
                    33.17719077971991,
                    33.135495887737314,
                    33.091794271180376,
                    33.04807092121569,
                    33.0341543908729,
                    32.8888939469936,
                ],
                "longitude_deg": [
                    -111.89522376678856,
                    -111.891090481453,
                    -111.88902383878514,
                    -111.89109048145292,
                    -111.89109048145292,
                    -111.89109048145292,
                    -111.8938809554476,
                    -111.8938809554476,
                    -111.8938809554476,
                    -111.91587509893408,
                    -111.92467275632866,
                    -111.9730598719989,
                    -111.959863385907,
                    -111.92583176190514,
                    -111.88788593455077,
                    -111.859426564035,
                    -111.82385235089023,
                    -111.7906497519552,
                    -111.774048452488,
                    -111.68867034094,
                ],
                "h_ft": [
                    0,
                    10,
                    40,
                    100,
                    140,
                    200,
                    280,
                    320,
                    410,
                    500,
                    560,
                    545,
                    470,
                    400,
                    280,
                    130,
                    100,
                    70,
                    20,
                    0,
                ],
            }
        }
