import CoolProp.CoolProp as CP
from STREAMS import Stream


def pump(S1_pump, P_out, efficiency):
    # Inlet enthalpy (J/kg)
    h1 = S1_pump.h
    # Discharge pressure (Pa)
    P2 = P_out
    # Calculating isentropic outlet enthalpy (J/kg)
    s2_ise = S1_pump.s
    h2_ise = CP.PropsSI('H', 'S', s2_ise, 'P',
                        P2, S1_pump.fluid)
    # Calculating outlet enthalpy (J/kg)
    h2 = (h1+((h2_ise-h1)/efficiency))
    # Calculating outlet temperature (K)
    T2 = CP.PropsSI('T', 'H', h2, 'P', P2, S1_pump.fluid)
    # Calculate outlet stream properties
    S2_pump = Stream(S1_pump.fluid)
    S2_pump.T = T2
    S2_pump.P = P2
    S2_pump.stream_porpeties_definition()

    # Calculating the specific fluid power,
    # also known as isentropic power (J/kg)
    w_ise = (h2_ise-h1)

    # Calculating the specific break power, also known as shaft power (J/kg)
    w_shaft = h2-h1

    # Calculating the specific exergy destruction (J/kg)
    e_d = S1_pump.e - S2_pump.e + w_shaft

    # Mass balance
    S2_pump.m = S1_pump.m

    return (S2_pump, w_ise, w_shaft, e_d)


def turbine(S1_turbine, efficiency, P_out=0, v_out=-1.0):
    # Inlet enthalpy (J/kg)
    h1 = S1_turbine.h
    # Discharge pressure (Pa)
    P2 = P_out
    # Calculating isentropic outlet enthalpy (J/kg)
    s2_ise = S1_turbine.s
    h2_ise = CP.PropsSI('H', 'S', s2_ise, 'P',
                        P2, S1_turbine.fluid)
    # Calculating outlet enthalpy (J/kg)
    h2 = h1-efficiency*(h1-h2_ise)
    # Calculating outlet temperature (K)
    T2 = CP.PropsSI('T', 'H', h2, 'P', P2, S1_turbine.fluid)
    # Calculate outlet stream properties
    S2_turbine = Stream(S1_turbine.fluid)
    S2_turbine.T = T2
    S2_turbine.P = P2
    # At the turbine outlet it is not known if the fluid
    # will be yet superheated or a liquid-vapor mixture.
    # To avoid error in the CP method, it is necessary to
    # caculate the vapor fraction priviuosly. If superheated,
    # CP method returns v=-1 and stream_porpeties_definition()
    # is already able to indetify which procedure
    # to execute, thus, avoinding errors
    v2 = CP.PropsSI('Q', 'H', h2, 'P', P2, S1_turbine.fluid)
    S2_turbine.v = v2
    S2_turbine.stream_porpeties_definition()

    # Calculating the specific fluid power,
    # also known as isentropic power (J/kg)
    w_ise = h1 - h2_ise

    # Calculating the specific break power, also known as shaft power (J/kg)
    w_shaft = h1 - h2

    # Calculating the specific exergy destruction (J/kg)
    e_d = S1_turbine.e - S2_turbine.e - w_shaft

    # Mass balance
    S2_turbine.m = S1_turbine.m

    return (S2_turbine, w_ise, w_shaft, e_d)
