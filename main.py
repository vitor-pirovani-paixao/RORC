from power_cycle import RORC_dry, RORC_dry_Tcon
import CoolProp.CoolProp as CP
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

if __name__ == '__main__':
    # Input data ###############################################
    # Working fluid
    working_fluid = 'Pentane'
    # Pump discharge pressure
    P2_pump = 30*10**5  # Pa
    # Pump isentropic efficiency
    efficiency_pump = 0.85
    # Turbine isentropic efficiency
    efficiency_turbine = 0.85
    # Hot fluid inlet temperature
    T1_hf_boiler = 480  # K
    # Hot fluid mass flow rate
    hf_massflow = 5  # kg/s

    # Working fluid outlet temperature at the condenser - Guess
    T2_wf_condenser = 40+273.15  # K
    # Stream 3 outlet enthalpy increase at the recuperator - Guess
    DH3 = 100  # J/kg
    x0 = np.zeros(2)
    x0[0] = T2_wf_condenser
    x0[1] = DH3
    # Finding real working fluid temperature ate condenser outlet so that
    # the condenser pinch point is equal to 10 K
    x_val = fsolve(RORC_dry_Tcon, x0,
                   args=(working_fluid, P2_pump,
                         efficiency_pump, efficiency_turbine,
                         T1_hf_boiler, hf_massflow))

    cycle_result = RORC_dry(float(x_val[0]), float(x_val[1]), working_fluid,
                            P2_pump, efficiency_pump, efficiency_turbine,
                            T1_hf_boiler, hf_massflow)
    # Stream array from power cycle simulation
    S = cycle_result[0]
    # Power cycle results
    eta_I = cycle_result[1]
    eta_II = cycle_result[2]
    Q_vec_cond = cycle_result[3]
    T_cw_cond = cycle_result[4]
    T_wf_cond = cycle_result[5]
    Q_vec_boiler = cycle_result[6]
    T_hf_boiler = cycle_result[7]
    T_wf_boiler = cycle_result[8]
    Q_vec_recuperator = cycle_result[9]
    T_cf_recuperator = cycle_result[10]
    T_hf_recuperator = cycle_result[11]

    # Displaying the results ########################################
    # T x S Diagram #################################################
    # Working fluid critical temperature
    T_critical = CP.PropsSI('Tcrit', working_fluid)
    # From 3 to 4
    # Finding evaporation temperature (K) and entropy (kJ/kg/K)
    T_evap_s3 = CP.PropsSI('T', 'P', S[2].P, 'Q', 0, working_fluid)

    # Temperature array from 273.15 K to T critical with 200 points
    T_range_vap = np.concatenate((np.linspace(273.15, T_critical-20, 100),
                                  np.linspace(T_critical-20, T_critical, 100)),
                                 axis=0)
    T_range_liq = np.concatenate((np.linspace(273.15, S[1].T, 50),
                                  np.linspace(T_evap_s3, T_critical, 200)),
                                 axis=0)
    # Specific entropy in kJ/kg/K
    s_liq = np.array([CP.PropsSI('S', 'T', T_range_liq[i],
                                 'Q', 0, working_fluid) /
                      1000 for i in range(T_range_liq.size)])
    s_vap = np.array([CP.PropsSI('S', 'T', T_range_vap[i],
                                 'Q', 1, working_fluid) /
                      1000 for i in range(T_range_vap.size)])
    plt.rcParams['font.sans-serif'] = ['Arial']  # Changing the figure's font
    plt.rcParams['legend.fontsize'] = 10  # Changing the legend fontsize
    plt.rcParams['font.size'] = 12  # Changing the figure's fontsize
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    # Adding data to the created axes of TxS diagram
    ax.plot(s_liq, T_range_liq, 'k')
    ax.plot(s_vap, T_range_vap, 'k', label=working_fluid)

    # Power Cycle T x S Diagram #######################################
    # From 1 to 2
    ax.plot([S[0].s/1000, S[1].s/1000], [S[0].T, S[1].T], 'r')
    # From 2 to 3
    if 0 <= S[2].v < 1:
        s_evap_s3 = CP.PropsSI('S', 'P', S[2].P, 'Q', 0, working_fluid)
        ax.plot([S[1].s/1000, s_evap_s3/1000, S[2].s/1000],
                [S[1].T, T_evap_s3, S[2].T], 'r')
    else:
        ax.plot([S[1].s/1000, S[2].s/1000], [S[1].T, S[2].T], 'r')
    # From 3 to 4
    if 0 <= S[2].v < 1:
        s_evap_s3b = CP.PropsSI('S', 'P', S[3].P, 'Q', 1, working_fluid)
        T_evap_s3b = CP.PropsSI('T', 'P', S[3].P, 'Q', 1, working_fluid)
        ax.plot([S[2].s/1000, s_evap_s3b/1000, S[3].s/1000],
                [S[2].T, T_evap_s3b, S[3].T], 'r')
    else:
        s_evap_s3 = CP.PropsSI('S', 'P', S[2].P, 'Q', 0, working_fluid)
        s_evap_s3b = CP.PropsSI('S', 'P', S[3].P, 'Q', 1, working_fluid)
        T_evap_s3b = CP.PropsSI('T', 'P', S[3].P, 'Q', 1, working_fluid)
        ax.plot([S[2].s/1000, s_evap_s3/1000, s_evap_s3b/1000, S[3].s/1000],
                [S[2].T, T_evap_s3, T_evap_s3b, S[3].T], 'r')
    # From 4 to 5
    ax.plot([S[3].s/1000, S[4].s/1000], [S[3].T, S[4].T], 'r')
    # From 5 to 6
    ax.plot([S[4].s/1000, S[5].s/1000], [S[4].T, S[5].T], 'r')
    # From 6 to 1
    # Finding condensation temperature (K) and entropy (kJ/kg/K)
    T_cond_s6 = CP.PropsSI('T', 'P', S[5].P, 'Q', 1, working_fluid)
    s_cond_s6 = CP.PropsSI('S', 'P', S[5].P, 'Q', 1, working_fluid)/1000
    ax.plot([S[5].s/1000, s_cond_s6, S[0].s/1000], [S[5].T, T_cond_s6,
                                                    S[0].T], 'r')
    plt.xlabel('Specific entropy (kJ/kg/K)')
    plt.ylabel('Temperature (K)')
    plt.title('Power Cycle Temperature x Entropy Diagram')
    plt.legend()  # To show legend in the figure

    fig1, ax1 = plt.subplots()  # Create a figure containing a single axes.
    ax1.plot(Q_vec_cond/1000, T_wf_cond, 'k', label=S[0].fluid)
    ax1.plot(Q_vec_cond/1000, T_cw_cond, 'b', label='Cooling water')
    plt.legend()  # To show legend in the figure
    plt.title('Composite Curve - Condenser')
    plt.xlabel('Heat rate (kW)')
    plt.ylabel('Temperature (K)')

    fig2, ax2 = plt.subplots()  # Create a figure containing a single axes.
    ax2.plot(Q_vec_boiler/1000, T_wf_boiler, 'k', label=S[0].fluid)
    ax2.plot(Q_vec_boiler/1000, T_hf_boiler, 'r', label='Saturated steam')
    plt.legend()  # To show legend in the figure
    plt.title('Composite Curve - Boiler')
    plt.xlabel('Heat rate (kW)')
    plt.ylabel('Temperature (K)')

    fig3, ax3 = plt.subplots()  # Create a figure containing a single axes.
    ax3.plot(Q_vec_recuperator/1000, T_cf_recuperator,
             'k', label='From 2 to 3')
    ax3.plot(Q_vec_recuperator/1000, T_hf_recuperator,
             'r', label='From 5 to 6')
    plt.legend()  # To show legend in the figure
    plt.title('Composite Curve - Recuperator')
    plt.xlabel('Heat rate (kW)')
    plt.ylabel('Temperature (K)')
    plt.show()  # To display the figure
