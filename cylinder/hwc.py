# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/20_hwc.ipynb.

# %% auto 0
__all__ = ['HWC']

# %% ../nbs/20_hwc.ipynb 3
from fastcore.utils import *
import pandas as pd
from .demand import load_demand
from .power import load_power
import matplotlib.pyplot as plt
import random
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# %% ../nbs/20_hwc.ipynb 5
class HWC():
  """
  Simple mixed model for a hot water cylinder
  """
  # Define constants for clearer code
  def __init__(self,
              element = 3, # Watts
              T_set = 65, # °C
              T_deadband = 2, # °C
              radius =.25,  # Meters
              height = 1, # Meters
              unit=None,  # Unit of measure for volume
              bedrooms=None,
              id = None):
    super(HWC, self).__init__()

    self.T_ambient = 15 #  Air temperature that the cylinder located in °C
    self.T_cold = 15 # Make up water temperature °C
    self.T_demand = 45 #T_demand - temperature of the end use (shower)  °C
    self.T_deadband = T_deadband #T_deadband  - thermostat deadband °C
    self.T_set = T_set #T_set - thermostat set point °C
    self.U = 0.8/60 # heat transfer coefficient 0.5 kJ/s m2K x 1/60 min/s [0.5 kJ/min m2K Jack Paper]
    self.Cp = 4.184 #kJ/kgK
    self.rho = 1000 #kg/m3
    self.surface_area = 2*np.pi*radius*height + 2*np.pi*radius**2 # m2
    self.volume = np.pi*radius**2*height
    self.element = element # kW = kJ/s
    self.heat_capacity = self.Cp*self.rho*self.volume # kJ/K
    self.thermostat = False
    self.bedrooms = bedrooms
    self.id = id
    self.reset()

# %% ../nbs/20_hwc.ipynb 7
@patch
def _thermostat(self:HWC):
    if (self.T < self.T_set- self.T_deadband) :
        self.thermostat = 1
    elif (self.T > self.T_set) :
        self.thermostat = 0
    return

# %% ../nbs/20_hwc.ipynb 10
@patch
def _update_temperatures(self:HWC, action = 1, ts = 60):
    '''
    Use the model from M Jack Paper to update the hwc temperature
    Takes existing state (temperature)
    '''
    temperature = self.T # existing temperatue of the cylinder
    temperature += (self.flow/self.volume)*(self.T_cold-self.T) * ts # change in temperature due to flow mixing
    self.Qi = (action * self.thermostat *  self.element )
    temperature += self.Qi / self.heat_capacity * ts # change in temperature due to element
    # kJ/s m2K x m2 / (kJ/K) x K x s = K
    # change in temperature due to heat loss
    temperature -= (self.U * self.surface_area) / self.heat_capacity * max(0,(self.T - self.T_ambient)) * ts / 60 # change in temperature due to heat loss
    return temperature

# %% ../nbs/20_hwc.ipynb 12
@patch
def reset(self:HWC):
    self.T = self.T_set + np.random.uniform(-4, 0)
    self.thermostat = 0
    multiplier = 2 if self.bedrooms is None else self.bedrooms
    self.thermogram = np.ones([7,24])*(.5+multiplier*.1)
