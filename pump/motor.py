import numpy as np
import math

class Motor():
    def __init__(self,nominal_voltage=440,nominal_current=19.2,nominal_speed=1800.0,nominal_torque=53,poles=4,nominal_cosphi=0.81,loadability_data=[[6,12,18,24,30,36,42,48,54,60],[0.71,0.76,0.81,0.85,0.87,0.89,0.91,0.93,0.95,0.85]]):
        self.nominal_voltage = float(nominal_voltage)
        self.nominal_current = float(nominal_current)
        self.nominal_speed = float(nominal_speed)
        self.nominal_torque = float(nominal_torque)
        self.poles = poles
        self.nominal_cosphi = float(nominal_cosphi)
        
        if loadability_data = None:
            loadability = lambda x: return 1
        else:   
            if type(loadability_data) != 'numpy.ndarray':
                loadability_data = np.array(loadability_data)
            loadability = interp1d(loadability_data[0,:],loadability_data[1,:],fill_value='extrapolate')

    def eta(self):
        return 0.9
        
    def cosphi(self):
        return nominal_cosphi
        
class MotorOperatingPoints():
    def __init__(self,speeds,torques,motor):
        speeds = np.array([speeds]).flatten()
        torques = np.array([torques]).flatten()
        
        if len(speeds) != len(torques):
            raise DimensionError('Speeds and torques must have same dimensions')
                    
        self.motor_operating_points = [MotorOperatingPoint(speed,torque,motor) for [speed,torque] in zip(speeds,torques)]
            
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
        return self.motor.cosphi())