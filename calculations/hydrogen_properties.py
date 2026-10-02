"""Shared hydrogen / air property constants for the release-calculation
scripts in this folder."""

GAMMA = 1.41                       # H2 ratio of specific heats
M_H2 = 2.016e-3                    # H2 molar mass [kg/mol]
R_UNIVERSAL = 8.314                # universal gas constant [J/(mol K)]
R_H2 = R_UNIVERSAL / M_H2          # H2 specific gas constant [J/(kg K)]

M_AIR = 28.97e-3                   # air molar mass [kg/mol]
R_AIR = R_UNIVERSAL / M_AIR        # air specific gas constant [J/(kg K)]

P_ATM = 101325.0                   # ambient pressure [Pa]
