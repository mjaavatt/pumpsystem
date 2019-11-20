from scipy import constants
import numpy as np
import math

class OperatingPoint(object):
    def __init__(self,flow,head,fluid):
        self.flow = flow
        self.head = head
        self.fluid = fluid

    @property
    def hydraulic_power(self):
        return self.flow*self.head*self.fluid.rho*constants.g

    def __str__(self):
        return "({},{})".format(self.head,self.flow)

class MotorOperatingPoint():
    def __init__(self,speed,torque,motor):
        self.speed = speed
        self.torque = torque
        self.motor = motor

    @property
    def shaft_power(self):
        return self.speed/60*2*math.pi * self.torque

    @property
    def electrical_power(self):
        return shaft_power*motor.eta()

    @property
    def voltage(self):
        return self.motor.nominal_voltage * self.speed / self.motor.nominal_speed

    @property
    def true_current(self):
        return self.electrical_power / ( self.voltage * math.sqrt(3))

    @property
    def apparent_current(self):
        return self.true_current / self.cosphi

    @property
    def cosphi(self):
        return self.motor.cosphi()

class PumpOperatingPoint(OperatingPoint):
    def __init__(self,head,flow,speed,pump):
        OperatingPoint.__init__(self,head,flow,pump.fluid)
        self.pump = pump
        self.speed = speed

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


class SystemCurveOperatingPoint(OperatingPoint):
    def __init__(self,head,flow,system_curve):
        OperatingPoint.__init__(self,head,flow,system_curve.fluid)
        self.system_curve = system_curve

class PumpSystemOperatingPoint(PumpOperatingPoint,SystemCurveOperatingPoint):
    def __init__(self,head,flow,pump,speed,system_curve):
        PumpOperatingPoint.__init__(self,head,flow,speed,pump)
        SystemCurveOperatingPoint.__init__(self,head,flow,system_curve)
