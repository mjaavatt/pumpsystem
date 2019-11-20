import numpy as np
import math
from fluid import Fluid
from operating_point import *
from scipy.interpolate import interp1d

from scipy import constants
from scipy.optimize import brentq,newton


class SystemCurve:
    """
    Simple quadratic process curve model.
    Example data provided for all parameters.

    Args:
        curve -- [c0,c1,c2] h = c0*q**2 + c1*q + c2, where h is head in meter and q is flow in m**3/s
    """
    def __init__(self,curve = None,nominal_speed=1800,fluid=Fluid()):
        self.c = np.array([9.6490e3,0,0])
        self.fluid = fluid
        if curve:
            self.c = curve

    def from_flow(self,flows):
        heads = np.polyval(self.c,flows)

        _heads = np.array([heads]).flatten()
        _flows = np.array([flows]).flatten()
        return [SystemCurveOperatingPoint(head,flow,self) for [head,flow] in zip(_heads,_flows)]

    def from_head(self,heads):
        p = np.poly1d(self.c)
        flows = np.max((p-heads).roots)
        _heads = np.array([heads]).flatten()
        _flows = np.array([flows]).flatten()
        return [SystemCurveOperatingPoint(head,flow,self) for [head,flow] in zip(_heads,_flows)]


class Pump(object):
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

    def __init__(self,curve = None,nominal_speed=1800,eta=[0],fluid=Fluid()):
        self.c0 = -6.6e3
        self.c1 = 27.0
        self.c2 = 19.0

        if curve:
            self.c0 = curve[0]
            self.c1 = curve[1]
            self.c2 = curve[2]
        self.n0 = nominal_speed
        self.fluid = fluid

    def from_flow(self,flow,speed):
        flow = np.array([flow]).flatten()
        speed = np.array([speed]).flatten()
        nominal_head = self.c0*flow**2 + self.c1*flow + np.ones(len(np.array(flow)))*self.c2
        head = (speed/float(self.n0))**2 * nominal_head

        _heads = np.array([head]).flatten()
        _flows = np.array([flow]).flatten()
        _speeds = np.array([speed]).flatten()

        return [PumpOperatingPoint(head,flow,speed,self) for [head,flow,speed] in zip(_heads,_flows,_speeds)]

    def from_head(self,head,speed):
        head = np.array([head]).flatten()
        head_at_n0 = (self.n0/float(speed))**2 * head
        nominal_flow = np.array([ max(np.roots([self.c0, self.c1, self.c2-x])) for x in head_at_n0])
        flow = (float(speed)/self.n0) * nominal_flow

        _heads = np.array([head]).flatten()
        _flows = np.array([flow]).flatten()
        _speeds = np.array([speed]).flatten()

        return [PumpOperatingPoint(head,flow,speed,self) for [head,flow,speed] in zip(_heads,_flows,_speeds)]

    def eta(self,flow,speed):
        return 0.6

class Motor():
    def __init__(self,nominal_voltage=440,nominal_current=19.2,nominal_speed=1800.0,nominal_torque=53,poles=4,nominal_cosphi=0.81,loadability_data=[[6,12,18,24,30,36,42,48,54,60],[0.71,0.76,0.81,0.85,0.87,0.89,0.91,0.93,0.95,0.85]]):
        self.nominal_voltage = float(nominal_voltage)
        self.nominal_current = float(nominal_current)
        self.nominal_speed = float(nominal_speed)
        self.nominal_torque = float(nominal_torque)
        self.poles = poles
        self.nominal_cosphi = float(nominal_cosphi)

        if loadability_data == None:
            self.loadability = lambda x: 1
        else:
            if type(loadability_data) != 'numpy.ndarray':
                loadability_data = np.array(loadability_data)
            self.loadability = interp1d(loadability_data[0,:],loadability_data[1,:],fill_value='extrapolate')

    def eta(self):
        return 0.9

    def cosphi(self):
        return nominal_cosphi



class PumpSystem:
    def __init__(self,pump=Pump(),system_curve=SystemCurve()):
        self.pump = pump
        self.system_curve = system_curve

        print("FIXME: Setting fluid to fluid from pump.")
        self.fluid = pump.fluid
        self.system_curve.fluid = pump.fluid

    def from_speed(self,speed):
        q = brentq(lambda q: self.pump.from_flow(q,speed)[0].flow - self.system_curve.from_flow(q)[0].flow ,0,1e99,maxiter=1000)
        operating_point = self.system_curve.from_flow(q)[0]
        return PumpSystemOperatingPoint(operating_point.head,operating_point.flow,self.pump,speed,self.system_curve)
