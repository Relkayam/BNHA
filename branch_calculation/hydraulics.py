import numpy as np


def calculate_head_loss(L, Q, C, d):
    """
    Calculate head loss using the Hazen–Williams equation.

    Parameters:
    L (float): Pipe length in meters.
    Q (float): Flow rate in cubic meters per second (m³/s).
    C (float): Hazen–Williams roughness coefficient (dimensionless).
    d (float): Pipe internal diameter in meters.

    Returns:
    float: Head loss in meters.

    Notes:
    - Returns 0 if flow (Q) or diameter (d) is non-positive.
    - Valid only for turbulent flow in pressurized pipes.
    """

    if Q <= 0 or d <= 0:
        return 0
    return (10.67 * L * Q**1.852) / (C**1.852 * d**4.8704)

def calculate_velocity(Q, d):
    """
    Compute average flow velocity in a circular pipe.

    Parameters:
    Q (float): Flow rate (m³/s).
    d (float): Pipe diameter (m).

    Returns:
    float: Velocity in meters per second (m/s).

    Notes:
    - Assumes full pipe flow.
    - Area is calculated as π * (d/2)^2.
    """

    if d <= 0:
        return 0
    area = np.pi * (d / 2)**2
    return Q / area

def calculate_reynolds_number(Q, d, kinematic_viscosity=1.004e-6):
    """
    Calculate Reynolds number for flow in a pipe.

    Parameters:
    Q (float): Flow rate (m³/s).
    d (float): Pipe diameter (m).
    kinematic_viscosity (float): Viscosity in m²/s (default is for water at 20°C).

    Returns:
    float: Reynolds number (dimensionless).

    Notes:
    - Helps determine if flow is laminar (<2000), transitional (2000–4000), or turbulent (>4000).
    """

    velocity = calculate_velocity(Q, d)
    return velocity * d / kinematic_viscosity
