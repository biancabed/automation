import numpy as np

# Physical constants
d = 1.3       # air density in kg/m³
cp = 0.593    # power coefficient (Betz limit)
eta_m = 0.98  # mechanical efficiency
eta_g = 0.99  # generator efficiency
t = 1         # operating time per data point (1 hour)

def calculate_energy(wind_speeds, rotor_area, number_of_turbines):
    # Mechanical power extracted from the wind
    Pm = 0.5 * d * rotor_area * (wind_speeds ** 3) * cp

    # Electrical power output from the generator
    Pe = Pm * eta_m * eta_g

    # Energy produced per turbine per hour
    We = Pe * t

    # Total energy produced by the entire wind farm
    We_farm = We * number_of_turbines

    # Sum over all hours and convert from Wh to MWh
    total_energy = We_farm.sum() / 1_000_000

    return total_energy
