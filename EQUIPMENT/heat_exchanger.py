import CoolProp.CoolProp as CP
from STREAMS import Stream
from COLOR import Color
import numpy as np


def boiler_dry_fluid_subcritical(S1_wf, S1_hf, S2_hf):
    # S1_wf is working fluid inlet stream
    # S1_hf is the heat source inlet stream
    # S2_hf is the heat source outlet stream

    # Boiler heat load
    Q = S1_hf.m*(S1_hf.h-S2_hf.h)  # (W)
    # Working fluid outlet stream
    S2_wf = Stream(S1_wf.fluid)
    # Pressure drop for vaporizing or condensing streams =10342 Pa
    # Seider pg 149
    S2_wf.P = S1_wf.P-10342  # Pa
    # Calculating working fluid saturation temperature at P2
    T2_sat_wf = (CP.PropsSI('T', 'P', S2_wf.P, 'Q', 1, S1_wf.fluid))  # K
    # Assumption from thesis: 5 K of superheating
    S2_wf.T = T2_sat_wf+5  # K
    if S2_hf.T < S2_wf.T + 10:
        print(Color.red, 'Pinch point violated at the boiler outlet.')
        print(f'Working fluid outlet temperature = {S2_wf.T}')
        print(f'Heat source inlet temperature = {S2_hf.T}')
        # Calulating the maximum allowed working fluid evaporation pressure
        T_max = S1_hf.T - 10  # 10 K pinch point
        T_sat_max = T_max - 5  # 10 K superheating
        P_max = (CP.PropsSI('P', 'T', T_sat_max, 'Q', 1, S1_wf.fluid))
        print(f'Maximum allowed pump dischrage pressure \
for {S1_wf.fluid} is {P_max/(10**5):.2f} bar', Color.white)

    S2_wf.stream_porpeties_definition()

    # Heat balance for working fluid
    # Working fluid mass flow rate
    S1_wf.m = Q/(S2_wf.h-S1_wf.h)  # kg/s
    S2_wf.m = S1_wf.m  # kg/s

    # Finding boiler pinch point...
    Np = 100
    Q_vec = np.linspace(0, Q, Np)
    P_hf = np.linspace(S1_hf.P, S2_hf.P, Np)
    P_wf = np.linspace(S1_wf.P, S2_wf.P, Np)
    T_hf = np.zeros(Np)
    T_wf = np.zeros(Np)
    h_hf = np.zeros(Np)
    h_wf = np.zeros(Np)
    for i in range(Np):
        if i == 0:
            T_wf[i] = S1_wf.T
            T_hf[Np-1-i] = S1_hf.T
            h_wf[i] = S1_wf.h
            h_hf[Np-1-i] = S1_hf.h
        else:
            h_wf[i] = Q_vec[1]/S1_wf.m + h_wf[i-1]
            T_wf[i] = CP.PropsSI('T', 'P', P_wf[i], 'H', h_wf[i], S1_wf.fluid)
            h_hf[Np-1-i] = h_hf[Np-i] - Q_vec[1]/S1_hf.m
            T_hf[Np-1-i] = CP.PropsSI('T', 'P', P_hf[i],
                                      'H', h_hf[Np-1-i],
                                      S1_hf.fluid)

    DT = np.zeros(Np)
    for i in range(Np):
        DT[i] = T_hf[i] - T_wf[i]

    return (S2_wf, Q, np.amin(DT), Q_vec, T_hf, T_wf)


def recuperator(S1_cf, S2_cf, S1_hf, S2_hf):
    # S1_cf is cold fluid inlet stream
    # S2_cf is cold fluid outlet stream
    # S1_hf is the hot fluid inlet stream
    # S2_hf is the hot fluid outlet stream

    # Recuperator heat load
    Q = S1_cf.m*(S2_cf.h-S1_cf.h)  # (W)

    # Heat balance for hot fluid
    # Hot fluid outlet temperature
    S2_hf.h = S1_hf.h-Q/S1_hf.m  # J/kg
    S2_hf.T = CP.PropsSI('T', 'P', S2_hf.P, 'H', S2_hf.h, S2_hf.fluid)
    S2_hf.v = CP.PropsSI('Q', 'P', S2_hf.P, 'H', S2_hf.h, S2_hf.fluid)
    S2_hf.stream_porpeties_definition()

    # Finding recuperator pinch point...
    Np = 30
    Q_vec = np.linspace(0, Q, Np)
    P_cf = np.linspace(S1_cf.P, S2_cf.P, Np)
    P_hf = np.linspace(S1_hf.P, S2_hf.P, Np)
    T_cf = np.zeros(Np)
    T_hf = np.zeros(Np)
    h_cf = np.zeros(Np)
    h_hf = np.zeros(Np)
    for i in range(Np):
        if i == 0:
            T_cf[i] = S1_cf.T
            T_hf[Np-1-i] = S1_hf.T
            h_cf[i] = S1_cf.h
            h_hf[Np-1-i] = S1_hf.h
        else:
            h_cf[i] = Q_vec[1]/S1_cf.m + h_cf[i-1]
            T_cf[i] = CP.PropsSI('T', 'P', P_cf[i], 'H', h_cf[i], S1_cf.fluid)
            h_hf[Np-1-i] = h_hf[Np-i] - Q_vec[1]/S1_hf.m
            T_hf[Np-1-i] = CP.PropsSI('T', 'P', P_hf[i],
                                      'H', h_hf[Np-1-i],
                                      S1_hf.fluid)

    DT = np.zeros(Np)
    for i in range(Np):
        DT[i] = T_hf[i]-T_cf[i]

    return (S2_hf, Q, np.amin(DT), Q_vec, T_cf, T_hf)


def boiler_dry_fluid_subcritical_rec(S1_wf, S1_hf, S2_hf):
    # S1_wf is working fluid inlet stream
    # S1_hf is the heat source inlet stream
    # S2_hf is the heat source outlet stream

    # Boiler heat load
    Q = S1_hf.m*(S1_hf.h-S2_hf.h)  # (W)
    # Working fluid outlet stream
    S2_wf = Stream(S1_wf.fluid)
    # Pressure drop for vaporizing or condensing streams =10342 Pa
    # Seider pg 149
    S2_wf.P = S1_wf.P-10342  # Pa
    # Calculating working fluid saturation temperature at P2
    T2_sat_wf = (CP.PropsSI('T', 'P', S2_wf.P, 'Q', 1, S1_wf.fluid))  # K
    # Assumption from thesis: 10 K bellow hot fluid inlet T
    S2_wf.T = S1_hf.T - 10  # K
    if S2_hf.T < T2_sat_wf + 5:
        print(Color.red, 'Minimum degree of superheating not achieved!')
        # Calulating the maximum allowed working fluid evaporation pressure
        T_sat_max = S2_wf.T - 5  # 5 K superheating
        P_max = (CP.PropsSI('P', 'T', T_sat_max, 'Q', 1, S1_wf.fluid))
        print(f'Maximum allowed pump dischrage pressure \
for {S1_wf.fluid} is {P_max/(10**5):.2f} bar', Color.white)

    S2_wf.stream_porpeties_definition()

    # Heat balance for working fluid
    # Working fluid mass flow rate
    S1_wf.m = Q/(S2_wf.h-S1_wf.h)  # kg/s
    S2_wf.m = S1_wf.m  # kg/s

    # Finding boiler pinch point...
    Np = 100
    Q_vec = np.linspace(0, Q, Np)
    P_hf = np.linspace(S1_hf.P, S2_hf.P, Np)
    P_wf = np.linspace(S1_wf.P, S2_wf.P, Np)
    T_hf = np.zeros(Np)
    T_wf = np.zeros(Np)
    h_hf = np.zeros(Np)
    h_wf = np.zeros(Np)
    for i in range(Np):
        if i == 0:
            T_wf[i] = S1_wf.T
            T_hf[Np-1-i] = S1_hf.T
            h_wf[i] = S1_wf.h
            h_hf[Np-1-i] = S1_hf.h
        else:
            h_wf[i] = Q_vec[1]/S1_wf.m + h_wf[i-1]
            T_wf[i] = CP.PropsSI('T', 'P', P_wf[i], 'H', h_wf[i], S1_wf.fluid)
            h_hf[Np-1-i] = h_hf[Np-i] - Q_vec[1]/S1_hf.m
            T_hf[Np-1-i] = CP.PropsSI('T', 'P', P_hf[i],
                                      'H', h_hf[Np-1-i],
                                      S1_hf.fluid)

    DT = np.zeros(Np)
    for i in range(Np):
        DT[i] = T_hf[i] - T_wf[i]

    return (S2_wf, Q, np.amin(DT), Q_vec, T_hf, T_wf)


def boiler_wet_fluid_subcritical(S1_wf, S1_hf, S2_hf):
    # S1_wf is working fluid inlet stream
    # S1_hf is the heat source inlet stream
    # S2_hf is the heat source outlet stream

    # Boiler heat load
    Q = S1_hf.m*(S1_hf.h-S2_hf.h)  # (W)
    # Working fluid outlet stream
    S2_wf = Stream(S1_wf.fluid)
    # Pressure drop for vaporizing or condensing streams =10342 Pa
    # Seider pg 149
    S2_wf.P = S1_wf.P-10342  # Pa
    # Calculating working fluid saturation temperature at P2
    T2_sat_wf = (CP.PropsSI('T', 'P', S2_wf.P, 'Q', 1, S1_wf.fluid))  # K
    # Assumption from thesis: 10 K bellow hot fliud inlet T
    S2_wf.T = S1_hf.T - 10  # K
    # Assumption from thesis: minimum 20 K of superheating must be provided
    if S2_wf.T < T2_sat_wf + 20:
        print(Color.red, 'Pump discharge pressure is too high!')
        print('Working fluid did not achieve the minimum degree of \
superheating (20 K)')
        # Calulating the maximum allowed working fluid evaporation pressure
        T_max = S1_hf.T - 10  # 10 K pinch point
        T_sat_max = T_max - 20  # 20 K superheating
        P_max = (CP.PropsSI('P', 'T', T_sat_max, 'Q', 1, S1_wf.fluid))
        print(f'Maximum allowed pump dischrage pressure \
for {S1_wf.fluid} is {P_max/(10**5):.2f} bar', Color.white)

    S2_wf.stream_porpeties_definition()

    # Heat balance for working fluid
    # Working fluid mass flow rate
    S1_wf.m = Q/(S2_wf.h-S1_wf.h)  # kg/s
    S2_wf.m = S1_wf.m  # kg/s

    # Finding boiler pinch point...
    Np = 100
    Q_vec = np.linspace(0, Q, Np)
    P_hf = np.linspace(S1_hf.P, S2_hf.P, Np)
    P_wf = np.linspace(S1_wf.P, S2_wf.P, Np)
    T_hf = np.zeros(Np)
    T_wf = np.zeros(Np)
    h_hf = np.zeros(Np)
    h_wf = np.zeros(Np)
    for i in range(Np):
        if i == 0:
            T_wf[i] = S1_wf.T
            T_hf[Np-1-i] = S1_hf.T
            h_wf[i] = S1_wf.h
            h_hf[Np-1-i] = S1_hf.h
        else:
            h_wf[i] = Q_vec[1]/S1_wf.m + h_wf[i-1]
            T_wf[i] = CP.PropsSI('T', 'P', P_wf[i], 'H', h_wf[i], S1_wf.fluid)
            h_hf[Np-1-i] = h_hf[Np-i] - Q_vec[1]/S1_hf.m
            T_hf[Np-1-i] = CP.PropsSI('T', 'P', P_hf[i],
                                      'H', h_hf[Np-1-i],
                                      S1_hf.fluid)

    DT = np.zeros(Np)
    for i in range(Np):
        DT[i] = T_hf[i] - T_wf[i]

    return (S2_wf, Q, np.amin(DT), Q_vec, T_hf, T_wf)


def condenser(S1_cw, S2_cw, S1_wf, S2_wf):
    # S1_wf is working fluid inlet stream
    # S2_wf is working fluid outlet stream
    # S1_cw is the cooling water inlet stream
    # S2_cw is the cooling water outlet stream

    # Condenser heat load
    Q = S1_wf.m*(S1_wf.h-S2_wf.h)  # (W)

    # Heat balance for cooling water
    # Working fluid mass flow rate
    S1_cw.m = Q/(S2_cw.h-S1_cw.h)  # kg/s
    S2_cw.m = S1_cw.m  # kg/s

    # Finding condenser pinch point...
    Np = 100
    Q_vec = np.linspace(0, Q, Np)
    P_cw = np.linspace(S1_cw.P, S2_cw.P, Np)
    P_wf = np.linspace(S1_wf.P, S2_wf.P, Np)
    T_cw = np.zeros(Np)
    T_wf = np.zeros(Np)
    h_cw = np.zeros(Np)
    h_wf = np.zeros(Np)
    for i in range(Np):
        if i == 0:
            T_cw[i] = S1_cw.T
            T_wf[Np-1-i] = S1_wf.T
            h_cw[i] = S1_cw.h
            h_wf[Np-1-i] = S1_wf.h
        else:
            h_cw[i] = Q_vec[1]/S1_cw.m + h_cw[i-1]
            T_cw[i] = CP.PropsSI('T', 'P', P_cw[i], 'H', h_cw[i], S1_cw.fluid)
            h_wf[Np-1-i] = h_wf[Np-i] - Q_vec[1]/S1_wf.m
            T_wf[Np-1-i] = CP.PropsSI('T', 'P', P_wf[i],
                                      'H', h_wf[Np-1-i],
                                      S1_wf.fluid)

    DT = np.zeros(Np)
    for i in range(Np):
        DT[i] = T_wf[i]-T_cw[i]

    return (S1_cw, S2_cw, Q, np.amin(DT), Q_vec, T_cw, T_wf)
