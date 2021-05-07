from EQUIPMENT import pump, turbine, condenser, recuperator
from EQUIPMENT import boiler_dry_fluid_subcritical_rec as boiler_DF_REC
from STREAMS import Stream
import numpy as np
import CoolProp.CoolProp as CP


def RORC_dry(T2_wf_condenser, DH3, working_fluid, P2_pump, efficiency_pump,
             efficiency_turbine, T1_hf_boiler, hf_flowrate):
    # Working fluid outlet vapor fraction at the condenser
    v2_wf_condenser = 0
    # Condenser outlet is pump inlet
    T1_pump = T2_wf_condenser
    v1_pump = v2_wf_condenser
    # Hot fluid vapor fraction at boiler inlet
    v1_hf_boiler = 1
    # Hot fluid inlet stream properties calculation
    S1_hf_boiler = Stream('Water')
    S1_hf_boiler.T = T1_hf_boiler
    S1_hf_boiler.v = v1_hf_boiler
    # Hot fluid mass flow rate
    S1_hf_boiler.m = hf_flowrate  # kg/s
    S1_hf_boiler.stream_porpeties_definition()
    # Hot fluid vapor fraction at boiler outlet
    v2_hf_boiler = 0
    # Pressure drop for vaporizing or condensing streams = 10342 Pa
    # Seider pg 149
    P2_hf_boiler = S1_hf_boiler.P - 10342  # Pa
    # Hot fluid outlet stream properties calculation
    S2_hf_boiler = Stream(S1_hf_boiler.fluid)
    S2_hf_boiler.P = P2_hf_boiler
    S2_hf_boiler.v = v2_hf_boiler
    S2_hf_boiler.stream_porpeties_definition()
    S2_hf_boiler.m = S1_hf_boiler.m

    # Pump ########################################################
    # Setting pump inlet stream properties
    S1_pump = Stream(working_fluid)
    S1_pump.T = T1_pump
    S1_pump.v = v1_pump
    S1_pump.stream_porpeties_definition()
    # Calculating pump variables
    Result_pump = pump(S1_pump, P2_pump, efficiency_pump)
    # Pump outlet stream
    S2_pump = Result_pump[0]
    # Pump specific isentropic power (J/kg)
    # w_ise_pump = Result_pump[1]
    # Pump specific shaft power (J/kg)
    w_shaft_pump = Result_pump[2]
    # Pump specific exergy destruction (J/kg)
    e_d_pump = Result_pump[3]

    # Recuperator - Part I #########################################
    # Pump outlet is Recupertor cold stream inlet
    S1_cf_recuperator = S2_pump
    # Setting cold stream (stream 3) outlet temperature
    S2_cf_recuperator = Stream(S1_cf_recuperator.fluid)
    S2_cf_recuperator.h = S1_cf_recuperator.h + DH3  # J/kg
    # Pressure drop for low viscosity fluids = 41368 Pa 6 psi
    # Seider pg 150
    S2_cf_recuperator.P = S1_cf_recuperator.P - 41368  # Pa
    S2_cf_recuperator.v = CP.PropsSI('Q', 'P', S2_cf_recuperator.P, 'H',
                                     S2_cf_recuperator.h,
                                     S1_cf_recuperator.fluid)
    S2_cf_recuperator.T = CP.PropsSI('T', 'P', S2_cf_recuperator.P, 'H',
                                     S2_cf_recuperator.h,
                                     S1_cf_recuperator.fluid)
    S2_cf_recuperator.stream_porpeties_definition()

    # Boiler ########################################################
    S1_wf_boiler = S2_cf_recuperator
    Result_boiler = boiler_DF_REC(
        S1_wf_boiler, S1_hf_boiler, S2_hf_boiler)
    # Working fluid outlet stream from the boiler
    S2_wf_boiler = Result_boiler[0]
    # Boiler heat duty (W)
    Q_boiler = Result_boiler[1]
    # Boiler pinch point
    Pinch_boiler = Result_boiler[2]
    # data to plot boiler hot and could fluid curves (pinch)
    Q_vec_boiler = Result_boiler[3]
    T_hf_boiler = Result_boiler[4]
    T_wf_boiler = Result_boiler[5]
    # Updating working fluid mass flow rate
    S1_pump.m = S2_wf_boiler.m
    S2_pump.m = S2_wf_boiler.m
    S1_wf_boiler.m = S2_wf_boiler.m

    # Turbine #######################################################
    S1_turbine = S2_wf_boiler
    # Pressure drop for vaporizing or condensing streams = 10342 Pa
    # Pressure drop for gaseous streams = 20684 Pa
    # Seider pg 149
    # Turbine outlet is recuperator inlet, which is condenser inlet, which
    # is pump inlet
    # Therefore, turbine outlet pressure will be pump's
    # inlet pressure + condenser pressure drop + recuperator pressure drop
    P_out_turbine = S1_pump.P+10342+20684  # Pa
    Result_turbine = turbine(S1_turbine, efficiency_turbine, P_out_turbine)
    # turbine outlet stream
    S2_turbine = Result_turbine[0]
    # turbine specific isentropic power (J/kg)
    # w_ise_turbine = Result_turbine[1]
    # turbine specific shaft power (J/kg)
    w_shaft_turbine = Result_turbine[2]
    # turbine specific exergy destruction (J/kg)
    e_d_turbine = Result_turbine[3]

    # Recuperator - Part II #########################################
    # Turbine outlet is Recupertor hot stream inlet
    S1_hf_recuperator = S2_turbine
    S2_hf_recuperator = Stream(S1_hf_recuperator.fluid)
    S2_hf_recuperator.m = S1_hf_recuperator.m
    # Pressure drop for gaseous streams = 20684 Pa
    # Seider pg 149
    S2_hf_recuperator.P = S1_hf_recuperator.P - 20684  # Pa

    Result_recuperator = recuperator(S1_cf_recuperator, S2_cf_recuperator,
                                     S1_hf_recuperator, S2_hf_recuperator)
    # Results recuperator
    S2_hf_recuperator = Result_recuperator[0]
    Q_rec = Result_recuperator[1]
    Pinch_rec = Result_recuperator[2]
    Q_vec_rec = Result_recuperator[3]
    T_cf_rec = Result_recuperator[4]
    T_hf_rec = Result_recuperator[5]

    # Condenser ######################################################
    # Setting cooling water information
    S1_cw_condenser = Stream('Water')
    S1_cw_condenser.P = 2*10**5  # Pa
    S1_cw_condenser.T = 25+273.15  # K
    S1_cw_condenser.stream_porpeties_definition()
    S2_cw_condenser = Stream(S1_cw_condenser.fluid)
    # Pressure drop for low viscosity fluids = 41368 Pa 6 psi
    # Seider pg 150
    S2_cw_condenser.P = 2*10**5 - 41368  # Pa
    S2_cw_condenser.T = 40+273.15  # K
    S2_cw_condenser.stream_porpeties_definition()
    # Working fluid streams
    S1_wf_condenser = S2_hf_recuperator
    S2_wf_condenser = S1_pump
    Result_condenser = condenser(
        S1_cw_condenser, S2_cw_condenser, S1_wf_condenser, S2_wf_condenser)
    # Updating Cooling streams information - with mass flow rate  now
    S1_cw_condenser = Result_condenser[0]
    S2_cw_condenser = Result_condenser[1]
    # Condenser heat duty (W)
    Q_condenser = Result_condenser[2]
    # Condenser pinch point
    Pinch_cond = Result_condenser[3]
    # data to plot condenser hot and could fluid curves (pinch)
    Q_vec_cond = Result_condenser[4]
    T_cw_cond = Result_condenser[5]
    T_wf_cond = Result_condenser[6]

    # Efficiencies ######################################################
    # Cycle efficiency 1st Law
    eta_I = (S1_pump.m*(w_shaft_turbine-w_shaft_pump)/Q_boiler)*100

    # Cycle efficiency 2nd Law Eq. 7.1.4
    # Exergy into the system
    E_in = ((S1_hf_boiler.e-S2_hf_boiler.e)*S1_hf_boiler.m)
    eta_IIa = 100*S1_pump.m*(w_shaft_turbine-w_shaft_pump)/E_in

    # Cycle efficiency 2nd Law Eq. 8.3.3
    # Exergy destruction boiler (W)
    E_d_boiler = S1_hf_boiler.m*S1_hf_boiler.e + \
        S1_wf_boiler.m*S1_wf_boiler.e - \
        S2_hf_boiler.m*S2_hf_boiler.e - S2_wf_boiler.m*S2_wf_boiler.e
    # Exergy destruction recuperator (W)
    E_d_recuperator = S1_hf_recuperator.m*S1_hf_recuperator.e + \
        S1_cf_recuperator.m*S1_cf_recuperator.e - \
        S2_hf_recuperator.m*S2_hf_recuperator.e - \
        S2_cf_recuperator.m*S2_cf_recuperator.e
    # Exergy destruction condenser (W)
    E_d_condenser = S1_cw_condenser.m*S1_cw_condenser.e + \
        S1_wf_condenser.m*S1_wf_condenser.e - \
        S2_cw_condenser.m*S2_cw_condenser.e - \
        S2_wf_condenser.m*S2_wf_condenser.e
    # Exergy destruction trubine (W)
    E_d_turbine = e_d_turbine*S1_turbine.m
    # Exergy destruction pump (W)
    E_d_pump = e_d_pump*S1_pump.m
    # Exergy loss cooling water (W)
    E_L_cw = (S2_cw_condenser.e-S1_cw_condenser.e)*S2_cw_condenser.m
    # Total exergy destruction + loss (W)
    E_dL_total = E_d_boiler + E_d_condenser + E_d_turbine + \
        E_d_recuperator + E_d_pump+E_L_cw

    eta_IIb = 100*(1-(E_dL_total/E_in))

    #  Saving cycle performance data...
    with open('CyclePerformance.txt', 'w') as cycle_perform:
        print(f'W_turbine (kW), \
{(w_shaft_turbine*S1_pump.m)/1000:.2f}', file=cycle_perform)
        print(f'W_pump (kW), \
{(w_shaft_pump*S1_pump.m)/1000:.2f}', file=cycle_perform)
        print(f'Q_boiler (kW), {Q_boiler/1000:.2f}', file=cycle_perform)
        print(f'Pinch_boiler (K), {Pinch_boiler:.2f}', file=cycle_perform)
        print(f'Q_recuperator (kW), {Q_rec/1000:.2f}', file=cycle_perform)
        print(f'Pinch_recuperator (K), {Pinch_rec:.2f}', file=cycle_perform)
        print(f'Q_condenser (kW), {Q_condenser/1000:.2f}', file=cycle_perform)
        print(f'Pinch_condenser (K), {Pinch_cond:.2f}', file=cycle_perform)
        print(f'Exer. destruc. + loss (kW), \
{E_dL_total/1000:.2f}', file=cycle_perform)
        print(f'Exergy destruction - Boiler (%), \
{100*E_d_boiler/E_dL_total:.2f}', file=cycle_perform)
        print(f'Exergy destruction - Recuperator (%), \
{100*E_d_recuperator/E_dL_total:.2f}', file=cycle_perform)
        print(f'Exergy destruction - Condenser (%), \
{100*E_d_condenser/E_dL_total:.2f}', file=cycle_perform)
        print(f'Exergy destruction - Pump (%),\
{100*E_d_pump/E_dL_total:.2f}', file=cycle_perform)
        print(
            f'Exergy destruction - Turbine (%), \
{100*E_d_turbine/E_dL_total:.2f}', file=cycle_perform)
        print(f'Exergy loss - Cooling water (%), \
{100*E_L_cw/E_dL_total:.2f}', file=cycle_perform)
        print(f'1st Law efficiency (%), {eta_I:.2f}', file=cycle_perform)
        print(f'2nd Law efficiency (%), {eta_IIa:.2f}', file=cycle_perform)
        print(f'2nd Law efficiency (%), {eta_IIb:.2f}', file=cycle_perform)

    # Organazing streams according to Fig. 8.1-a in thesis
    S = [S1_pump, S2_pump, S2_cf_recuperator, S2_wf_boiler, S2_turbine,
         S2_hf_recuperator, S1_cw_condenser, S2_cw_condenser, S1_hf_boiler,
         S2_hf_boiler]

    # Saving stream data...
    with open('StreamData.txt', 'w') as stream_data:
        for i in range(len(S)+1):
            if i == 0:
                print('Stream  Temperature (K)  Pressure (kPa)  Vap. Frac.  \
Enthalpy (kJ/kg)  Entropy (kJ/kg/K)  Exergy (kJ/kg)  Mass flow rate (kg/s)  \
Fluid', file=stream_data)
            else:
                print(f'S{i:<7}{S[i-1].T:<17.2f}{S[i-1].P/(10**3):<16.2f}\
{S[i-1].v:<12.2f}{S[i-1].h/(10**3):<18.2f}{S[i-1].s/(10**3):<19.2f}\
{S[i-1].e/(10**3):<16.2f}{S[i-1].m:<23.2f}{S[i-1].fluid}', file=stream_data)

    return [S, eta_I, eta_IIa, Q_vec_cond, T_cw_cond, T_wf_cond,
            Q_vec_boiler, T_hf_boiler, T_wf_boiler, Q_vec_rec,
            T_cf_rec, T_hf_rec]


def RORC_dry_Tcon(x0, working_fluid, P2_pump,
                  efficiency_pump, efficiency_turbine,
                  T1_hf_boiler, hf_flowrate):
    # Working fluid outlet vapor fraction at the condenser
    v2_wf_condenser = 0
    # Condenser outlet is pump inlet
    T1_pump = float(x0[0])
    v1_pump = v2_wf_condenser
    # Hot fluid vapor fraction at boiler inlet
    v1_hf_boiler = 1
    # Hot fluid inlet stream properties calculation
    S1_hf_boiler = Stream('Water')
    S1_hf_boiler.T = T1_hf_boiler
    S1_hf_boiler.v = v1_hf_boiler
    # Hot fluid mass flow rate
    S1_hf_boiler.m = hf_flowrate  # kg/s
    S1_hf_boiler.stream_porpeties_definition()
    # Hot fluid vapor fraction at boiler outlet
    v2_hf_boiler = 0
    # Pressure drop for vaporizing or condensing streams = 10342 Pa
    # Seider pg 149
    P2_hf_boiler = S1_hf_boiler.P - 10342  # Pa
    # Hot fluid outlet stream properties calculation
    S2_hf_boiler = Stream(S1_hf_boiler.fluid)
    S2_hf_boiler.P = P2_hf_boiler
    S2_hf_boiler.v = v2_hf_boiler
    S2_hf_boiler.stream_porpeties_definition()
    S2_hf_boiler.m = S1_hf_boiler.m

    # Pump ########################################################
    # Setting pump inlet stream properties
    S1_pump = Stream(working_fluid)
    S1_pump.T = T1_pump
    S1_pump.v = v1_pump
    S1_pump.stream_porpeties_definition()
    # Calculating pump variables
    Result_pump = pump(S1_pump, P2_pump, efficiency_pump)
    # Pump outlet stream
    S2_pump = Result_pump[0]

    # Recuperator - Part I #########################################
    # Pump outlet is Recupertor cold stream inlet
    S1_cf_recuperator = S2_pump
    # Setting cold stream (stream 3) outlet temperature
    S2_cf_recuperator = Stream(S1_cf_recuperator.fluid)
    S2_cf_recuperator.h = S1_cf_recuperator.h + float(x0[1])
    # Pressure drop for low viscosity fluids = 41368 Pa 6 psi
    # Seider pg 150
    S2_cf_recuperator.P = S1_cf_recuperator.P - 41368  # Pa
    S2_cf_recuperator.v = CP.PropsSI('Q', 'P', S2_cf_recuperator.P, 'H',
                                     S2_cf_recuperator.h,
                                     S1_cf_recuperator.fluid)
    S2_cf_recuperator.T = CP.PropsSI('T', 'P', S2_cf_recuperator.P, 'H',
                                     S2_cf_recuperator.h,
                                     S1_cf_recuperator.fluid)
    S2_cf_recuperator.stream_porpeties_definition()

    # Boiler ########################################################
    S1_wf_boiler = S2_cf_recuperator
    Result_boiler = boiler_DF_REC(
        S1_wf_boiler, S1_hf_boiler, S2_hf_boiler)
    # Working fluid outlet stream from the boiler
    S2_wf_boiler = Result_boiler[0]
    # Updating working fluid mass flow rate
    S1_pump.m = S2_wf_boiler.m
    S2_pump.m = S2_wf_boiler.m
    S1_wf_boiler.m = S2_wf_boiler.m

    # Turbine #######################################################
    S1_turbine = S2_wf_boiler
    # Pressure drop for vaporizing or condensing streams = 10342 Pa
    # Pressure drop for gaseous streams = 20684 Pa
    # Seider pg 149
    # Turbine outlet is recuperator inlet, which is condenser inlet, which
    # is pump inlet
    # Therefore, turbine outlet pressure will be pump's
    # inlet pressure + condenser pressure drop + recuperator pressure drop
    P_out_turbine = S1_pump.P+10342+20684  # Pa
    Result_turbine = turbine(S1_turbine, efficiency_turbine, P_out_turbine)
    # turbine outlet stream
    S2_turbine = Result_turbine[0]

    # Recuperator - Part II #########################################
    # Turbine outlet is Recupertor hot stream inlet
    S1_hf_recuperator = S2_turbine
    S2_hf_recuperator = Stream(S1_hf_recuperator.fluid)
    S2_hf_recuperator.m = S1_hf_recuperator.m
    # Pressure drop for gaseous streams = 20684 Pa
    # Seider pg 149
    S2_hf_recuperator.P = S1_hf_recuperator.P - 20684  # Pa

    Result_recuperator = recuperator(S1_cf_recuperator, S2_cf_recuperator,
                                     S1_hf_recuperator, S2_hf_recuperator)
    # Results recuperator
    S2_hf_recuperator = Result_recuperator[0]
    DTmin_recuperator = Result_recuperator[2]

    # Condenser ######################################################
    # Setting cooling water information
    S1_cw_condenser = Stream('Water')
    S1_cw_condenser.P = 2*10**5  # Pa
    S1_cw_condenser.T = 25+273.15  # K
    S1_cw_condenser.stream_porpeties_definition()
    S2_cw_condenser = Stream(S1_cw_condenser.fluid)
    # Pressure drop for low viscosity fluids = 41368 Pa 6 psi
    # Seider pg 150
    S2_cw_condenser.P = 2*10**5 - 41368  # Pa
    S2_cw_condenser.T = 40+273.15  # K
    S2_cw_condenser.stream_porpeties_definition()
    # Working fluid streams
    S1_wf_condenser = S2_hf_recuperator
    S2_wf_condenser = S1_pump
    Result_condenser = condenser(
        S1_cw_condenser, S2_cw_condenser, S1_wf_condenser, S2_wf_condenser)
    # Updating Cooling streams information - with mass flow rate  now
    S1_cw_condenser = Result_condenser[0]
    S2_cw_condenser = Result_condenser[1]
    # Condenser pinch point
    DTmin_cond = Result_condenser[3]

    # Objective funtion
    F = np.zeros(2)
    F[0] = DTmin_cond-10
    F[1] = DTmin_recuperator-10

    return F
