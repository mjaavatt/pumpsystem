import numpy as np
import math
from scipy import constants

class Pump:
    """
    Simple quadratic pump curve model.
    Example data provided for all parameters.

    Args:
        curve -- [c0,c1,c2] h = c0*q**2 + c1*q + c2, where h is head in meter and q is flow in m**3/s
        nominal_speed -- rotational speed in rpm for curv (default = 1800)
        eta --  [e0,e1,e2] Hydraulic efficiency eta = e0*q**2 + e1*q + e2
        rho -- Fluid density (default = 1000 kg/m**3)


    Speed scaling according to standard centrifugal pump affinity laws:

    (h1/h2)**2 = (n1/n2)

    Hydraulic efficiency scaling:

    None
    """

    def __init__(self,curve = None,nominal_speed=1800,eta=[0],rho=1000):
        self.c0 = -6.6e3
        self.c1 = 27.0
        self.c2 = 19.0

        if curve:
            self.c0 = curve[0]
            self.c1 = curve[1]
            self.c2 = curve[2]
        self.n0 = nominal_speed
        self.rho = rho

    def from_flow(self,flow,speed):
        flow = np.array([flow]).flatten()
        speed = np.array([speed]).flatten()
        nominal_head = self.c0*flow**2 + self.c1*flow + np.ones(len(np.array(flow)))*self.c2
        head = (speed/float(self.n0))**2 * nominal_head
        return PumpOperatingPoints(head,flow,speed,self)


    def from_head(self,head,speed):
        head = np.array([head]).flatten()
        head_at_n0 = (self.n0/float(speed))**2 * head
        #nominal_flow = max(np.roots([self.c0, self.c1, self.c2-head_at_n0]))
        nominal_flow = np.array([ max(np.roots([self.c0, self.c1, self.c2-x])) for x in head_at_n0])
        flow = (float(speed)/self.n0) * nominal_flow
        return PumpOperatingPoints(head,flow,speed,self)

    def eta(self,flow,speed):
        return 0.6

class PumpOperatingPoints():
    def __init__(self,heads,flows,speeds,pump):
        flows = np.array([flows]).flatten()
        speeds = np.array([speeds]).flatten()
        heads = np.array([heads]).flatten()

        if len(flows) != len(heads):
            raise DimensionError('Flows and heads must have same dimensions')

        if len(speeds) == 1:
            speeds = np.ones(len(flows))*speeds

        if len(speeds) != len(heads):
            raise DimensionError('speeds must have same dimensions as flows and heads')


        self.pump_operating_points = [PumpOperatingPoint(head,flow,speed,pump) for [head,flow,speed] in zip(heads,flows,speeds)]

    def heads(self):
        return [pump_operating_point.head for pump_operating_point in self.pump_operating_points]

    def flows(self):
        return [pump_operating_point.flow for pump_operating_point in self.pump_operating_points]

    def hydraulic_powers(self):
        return [pump_operating_point.hydraulic_power for pump_operating_point in self.pump_operating_points]

    def shaft_powers(self):
        return [pump_operating_point.shaft_power for pump_operating_point in self.pump_operating_points]

    def shaft_torques(self):
        return [pump_operating_point.shaft_torque for pump_operating_point in self.pump_operating_points]

    def etas(self):
        return [pump_operating_point.eta for pump_operating_point in self.pump_operating_points]

    def __str__(self):
        return ','.join([str(pump_operating_point) for pump_operating_point in self.pump_operating_points])

class PumpOperatingPoint():
    def __init__(self,head,flow,speed,pump):
        self.pump = pump
        self.flow = flow
        self.head = head
        self.speed = speed

    @property
    def hydraulic_power(self):
        return self.flow*self.head*self.pump.rho*constants.g

    @property
    def eta(self):
        return self.pump.eta(self.flow,self.speed)

    @property
    def shaft_power(self):
        return self.hydraulic_power/self.eta

    @property
    def shaft_torque(self):
        return self.shaft_power / ((self.speed/60)*(2*math.pi))

    def __str__(self):
        return "({},{},{})".format(self.head,self.flow,self.speed)
