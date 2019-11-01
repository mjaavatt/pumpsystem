import numpy as np
import math
from scipy import constants

class ProcessCurve:
    """
    Simple quadratic process curve model.
    Example data provided for all parameters.

    Args:
        curve -- [c0,c1,c2] h = c0*q**2 + c1*q + c2, where h is head in meter and q is flow in m**3/s
    """
    def __init__(self,curve = None,nominal_speed=1800,rho=1000):
        self.c = np.array([9.6490e3,0,0])
        self.rho = rho

        if curve:
            self.c = curve


    def heads(self,flows):
        heads = np.polyval(self.c,flows)

        return OperatingPoints(heads,flows,self)

    def flows(self,heads):
        p = np.poly1d(self.c)
        flows = np.max((p-heads).roots)
        return OperatingPoints(heads,flows,self)

class OperatingPoints():
    def __init__(self,heads,flows,process_curve):
        flows = np.array([flows]).flatten()
        heads = np.array([heads]).flatten()

        if len(flows) != len(heads):
            raise DimensionError('Flows and heads must have same dimensions')

        self.operating_points = [OperatingPoint(head,flow,process_curve) for [head,flow] in zip(heads,flows)]

    def heads(self):
        return [operating_point.head for operating_point in self.operating_points]

    def flows(self):
        return [operating_point.flow for operating_point in self.operating_points]

class OperatingPoint():
    def __init__(self,head,flow,process_curve):
        self.process_curve = process_curve
        self.flow = flow
        self.head = head

    @property
    def hydraulic_power(self):
        return self.flow*self.head*self.process_curve.rho*constants.g

    def __str__(self):
        return "({},{},{})".format(self.head,self.flow)
