import errno
import CoolProp.CoolProp as CP


class Stream():
    def __init__(self, fluid):
        self.T = float()  # K
        self.P = float()  # Pa
        self.v = -1.0     # Vap. frac.
        self.h = float()  # J/kg
        self.s = float()  # J/kg/K
        self.e = float()  # J/kg
        self.m = float()  # kg/s
        self.fluid = fluid

    def stream_porpeties_definition(self):
        # Reference state for exergetic calculations
        P0 = 101325  # Pa
        T0 = 298.15  # K

        if 0 <= self.v <= 1:
            if self.T != 0.0:
                # Specific entropy (J/kg/K)
                self.s = CP.PropsSI('S', 'T', self.T,
                                    'Q', self.v, self.fluid)
                # Specific enthalpy (J/kg)
                self.h = (CP.PropsSI('H', 'T', self.T,
                                     'Q', self.v, self.fluid))
                # Pressure (Pa)
                self.P = (CP.PropsSI('P', 'T', self.T,
                                     'Q', self.v, self.fluid))
                # Specific exergy (J/kg)
                h0 = (CP.PropsSI('H', 'T', T0, 'P', P0, self.fluid))  # J/kg
                s0 = (CP.PropsSI('S', 'T', T0, 'P', P0, self.fluid))  # J/kg/K
                self.e = (self.h-h0)-T0*(self.s-s0)
                return self
            elif self.P != 0.0:
                # Specific entropy (J/kg/K)
                self.s = CP.PropsSI('S', 'P', self.P,
                                    'Q', self.v, self.fluid)
                # Specific enthalpy (J/kg)
                self.h = (CP.PropsSI('H', 'P', self.P,
                                     'Q', self.v, self.fluid))
                # Temperature (Pa)
                self.T = (CP.PropsSI('T', 'P', self.P,
                                     'Q', self.v, self.fluid))
                # Specific exergy (J/kg)
                h0 = (CP.PropsSI('H', 'T', T0, 'P', P0, self.fluid))  # J/kg
                s0 = (CP.PropsSI('S', 'T', T0, 'P', P0, self.fluid))  # J/kg/K
                self.e = (self.h-h0)-T0*(self.s-s0)
                return self
            else:
                print('Please, provide either P or T')
        elif self.T != 0 and self.P != 0:
            # Specific entropy (J/kg/K)
            self.s = CP.PropsSI('S', 'T', self.T,
                                'P', self.P, self.fluid)
            # Specific enthalpy (J/kg)
            self.h = (CP.PropsSI('H', 'T', self.T,
                                 'P', self.P, self.fluid))
            # Vapor fraction
            self.v = (CP.PropsSI('Q', 'T', self.T,
                                 'P', self.P, self.fluid))
            # Specific exergy (J/kg)
            h0 = (CP.PropsSI('H', 'T', T0, 'P', P0, self.fluid))  # J/kg
            s0 = (CP.PropsSI('S', 'T', T0, 'P', P0, self.fluid))  # J/kg/K
            self.e = (self.h-h0)-T0*(self.s-s0)
            return self
        else:
            print('Please, provide at least 2 of the following: P, T and v')
            print('If you choose to provide "v", it must be 0 <= v <= 1')
            print('Otherwaise, provide P and T')
            return errno.EINVAL
