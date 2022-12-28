# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/20_hwc_2node.ipynb.

# %% auto 0
__all__ = ['HWC']

# %% ../nbs/20_hwc_2node.ipynb 3
from fastcore.utils import *
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# %% ../nbs/20_hwc_2node.ipynb 6
class HWC():
  """
  Model of a Hot Water Cylinder using a nodal approach.
  """
  def __init__(self,
              element = 3,        # kW
              T_set = 75,         # °C
              T_deadband = 2,     # °C
              T_cold = 15,     # °C
              T_inlet = 15,     # °C
              radius =.25,        # m
              height = 1.1,       # m
              K = 0.05,       # m
              U = 0.8,
              mixed = False,
              noisey = True):
    super(HWC, self).__init__()
    self.U = U/60 #0.0019678 #U/60     # 0.5-0.8 kJ/min m2K typical heat transfer losses to ambient  [0.5 kJ/min m2K Jack Paper] kW/m2K
    self.split = np.array([2/3,1/3])
    self.Cv = 4.184 #kJ/kgK
    self.ρ = 1000 #kg/m3
    self.T_ambient = 15 #  Air temperature that the cylinder located in °C
    self.T_cold = T_cold # Make up water temperature °C to mixer
    self.T_inlet = T_inlet # Make up water temperature °C
    self.T_demand = 45 #T_demand - temperature of the end use (shower)  °C
    self.T_deadband = T_deadband #T_deadband  - thermostat deadband °C
    self.T_set = T_set #T_set - thermostat set point °C
    self.element = element # kW = kJ/s
    self.radius = radius
    self.height = height
    self.T_set_bu = 60
    self.flow = 0
    self.z = self.z_init
    self.K = K
    self.mixed = mixed
    temperature = self.T_set + np.random.uniform(-5, 0)
    if noisey:
      self.temperatures = np.array([temperature,temperature+ np.random.uniform(-5, 0)])
    else:
      self.temperatures = np.array([self.T_set -1.0, self.T_set-4.0])
    self.thermostat = np.array([0,0]) # bulk / nodal high / nodal low

    self.temperatures_ = self.temperatures
    self.stratified = True
    if mixed:
      self.stratified = False
      self.temperatures = np.array([temperature,temperature])
      self.thermostat = np.array([0,0])
    # self._thermostat()
    
  @property
  def volume(self): return np.pi * self.radius ** 2 * self.height  # m3

  @property
  def A(self): return np.pi * self.radius**2 # m2 

  @property
  def cylinder_wall_area(self): return 2* np.pi * self.radius * self.height  # m2 

  @property
  def surface_area(self): return self.cylinder_wall_area + 2 * self.A # m2 

  @property
  def U_ends(self): 
    return self.U * self.A   / (self.Cv * self.volume * self.ρ)# unit  heat transfer coefficient kW/K
  
  @property
  def U_cylinder(self): 
    return self.U * self.cylinder_wall_area  / (self.Cv * self.volume * self.ρ) # unit  heat transfer coefficient kW/K  
  
  @property
  def z_init(self): 
    return .7  # initial thermocline level from the top of the cylinder

  @property
  def temperature(self): 
    if self.stratified:
      return self.temperatures[0]*self.z + self.temperatures[1]*(1-self.z)
    else:
      return self.temperatures[0]


# %% ../nbs/20_hwc_2node.ipynb 12
@patch
def _update_model(self:HWC, action = 0, flow = 0, timestep = 60): 
    # the demand flow is at the temperature of the end use (shower) °C after the themostatic mixing valve and this requires adjustment to compenstate for the outlet temperature of the cylinder
    tempered_flow = (flow*(self.T_demand-self.T_cold) /(self.temperatures[0]-self.T_cold).clip(min=0))
    f_t = tempered_flow / self.volume
    q_t = action * self.element * timestep / (self.Cv * self.volume * self.ρ)

    if self.mixed:
        self.temperatures[0] += (f_t *(self.T_inlet - self.temperatures.mean()) + \
                                action * self.element * timestep / (self.Cv * self.volume * self.ρ) - \
                               (2*self.U_ends + self.U_cylinder)/ (self.Cv * self.volume * self.ρ) *(self.temperatures.mean() - self.T_ambient))
        self.temperatures[1] = self.temperatures[0]
        return

    if self.stratified:
        self.temperatures[0] += -((self.U_ends + self.U_cylinder * self.z) * (self.temperatures[0] - self.T_ambient) + self.K * self.A) /self.z
        self.temperatures[1] += (f_t * (self.T_inlet - self.temperatures[1]) + \
                                q_t - \
                                (self.U_ends + self.U_cylinder * (1-self.z))*(self.temperatures[1] - self.T_ambient)+ self.K * self.A) /(1-self.z)
        self.z -= f_t
    else: 
        self.temperatures[0] += (f_t *(self.T_inlet - self.temperatures.mean()) + \
                                q_t - \
                               (2*self.U_ends + self.U_cylinder)*(self.temperatures.mean() - self.T_ambient))
        self.temperatures[1] = self.temperatures[0]
    # test for change in state
    if (self.flow == 0) and (flow > 0): # change to state (ii) i.e. from fully mixed to stratified
        self.z = self.z_init
        self.stratified = True
    
    if (self.temperatures[1]>self.temperatures[0]) or self.z <=0 or self.z >=1 and not self.mixed:
        self.stratified = False
        self.temperatures[0] = self.temperatures[0]* self.z + self.temperatures[1] * (1-self.z) 
        self.temperatures[1] = self.temperatures[0]

