# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_utils.ipynb.

# %% auto 0
__all__ = ['get_season', 'series_timestamps', 'plot_sim']

# %% ../nbs/99_utils.ipynb 3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime, timedelta
from scipy.stats import skew, skewnorm
import random
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# %% ../nbs/99_utils.ipynb 4
def get_season(date):
  month = date.month
  if month  >= 3 and month <= 5:
    return "Autumn"
  elif month >= 6 and month <= 8:
    return "Winter"
  elif month >= 9 and month <= 11:
    return "Spring"
  else:
    return "Summer"

# %% ../nbs/99_utils.ipynb 5
def series_timestamps(ser):
    result = []
    start, end = None , None
    # Loop through the input list
    for row in ser.iteritems():
        # If we encounter a 1, update the start and end index if needed
        if row[1] == 1:
            if start is None:
                start = row[0]
            end = row[0]
        # If we encounter a 0, append the start and end index to the result
        # and reset the start and end index
        elif row[1] == 0 and start is not None:
            result.append((start, end))
            start = None
            end = None

    # If the last element of the input list is a 1, we need to append
    # the start and end index to the result one more time
    if start is not None:
        result.append((start, end))
    return result

# %% ../nbs/99_utils.ipynb 6
def plot_sim(strategy, df):
    fig, ax = plt.subplots(nrows=4,figsize=(18,6), sharey="row", gridspec_kw=dict(height_ratios=[.2,.2,.2,3], hspace=0))
    i=0
    # Plot flow data
    im2 = ax[i].imshow(df.energy.values[np.newaxis,:], cmap="viridis", aspect="auto", vmin=0, vmax=18)
    ax[i].set_yticks([])
    ax[i].set_xticks([])

    ax[i].set_ylabel('Energy', rotation=0, fontsize=8)
    ax[i].yaxis.set_label_coords(-0.03,.2)
    i=1
    # Plot flow data
    ax[i].imshow(df.flow.values[np.newaxis,:], cmap="Reds", aspect="auto")
    ax[i].set_yticks([])
    ax[i].set_xticks([])

    ax[i].set_ylabel('Flow', rotation=0, fontsize=8)
    ax[i].yaxis.set_label_coords(-0.03,.2)
    
    i=2
     # Plot flow data
    im = ax[i].imshow(df.cost.values[np.newaxis,:], cmap="jet", aspect="auto")
    ax[i].set_yticks([])
    ax[i].set_xticks([])
    ax[i].set_ylabel('Cost', rotation=0, fontsize=8)
    ax[i].yaxis.set_label_coords(-0.03,.2)



    # add title
    title = f'Simulation:'+ strategy['name'] + '\n' +\
            'mode : ' + strategy['operation'] + ' | ' +\
            'bedrooms : ' + str(strategy['bedrooms']) + '\n' +\
            'element : ' + str(strategy['element']) + 'kW | ' +\
            'ripple : ' + str(strategy['ripple'])
    i=3
    # ax.plot(df.action*1)
    for j in range(2):
        ax[i].plot(df[f'T{j}'], label=f'T{j}')
    ax[i].set_ylim(50,83)
    # ax[0].set_title('Temperature')
    ax[i].set_ylabel('°C', rotation=90)
    ax[i].margins(x=0, y=0)
    ax[i].axhline(y=55, color='k', linestyle='--', alpha = .5)

    # if strategy['Tset_H'] != strategy['Tset_L']:
    #     ax[i].axhspan(strategy['Tset_H']-2, strategy['Tset_H'],0,.1,  color='mistyrose', alpha=0.4) # wants power but ripple control is on
    #     ax[i].annotate('Upper Thermostat', xy=(0, 0.75), xycoords='axes fraction',  xytext=(5, 0), textcoords='offset points', ha="left", va="top", fontsize=8)


    # ax[i].axhspan(strategy['Tset_L']-2, strategy['Tset_L'],0,.1,  color='powderblue', alpha=0.4) # wants power but ripple control is on

    for k in series_timestamps((df.thermostat_base == 1)&(df.ripple_control)&(strategy['ripple'])): ax[i].axvspan(k[0], k[1], 0.08, .13, color='red', alpha=0.5, hatch ='\\', ec='black') # wants power but ripple control is on
    for k in series_timestamps((df.thermostat_base == 1)&(df.ripple_control)&(~strategy['ripple'])): ax[i].axvspan(k[0], k[1], 0.08, .13, color='blue', alpha=0.5) # wants power but ripple control is on
    for k in series_timestamps((df.thermostat_base == 1)&(df.ripple_control)&(~strategy['ripple'])): ax[i].axvspan(k[0], k[1], 0.08, .13, color='blue', alpha=0.5) # wants power but ripple control is on
    for k in series_timestamps((df.thermostat_base == 1)&(~df.ripple_control)): ax[i].axvspan(k[0], k[1], 0.08, .13, color='green', alpha=0.5)
    for k in series_timestamps((df.action == 1)&(df.thermostat_high == 1)&(~strategy['ripple'])&(df.thermostat_base == 0)): ax[i].axvspan(k[0], k[1],  0.08, .13,color='cyan', alpha=0.5)
    
    
    operation_legend = [Patch(facecolor='red', hatch ='\\', ec='black', alpha=0.5 , label='Demand / No Power'),
                      Patch(facecolor='blue', alpha=0.5 ,  label='Operation during Ripple Control'),
                      Patch(facecolor='cyan', alpha=0.5 ,  label='Boost Operation'),
                      Patch(facecolor='green', alpha=0.5 ,   label='Base Operation')]

    ax[i].axhline(y=55, color='k', linestyle='--', alpha = .5)

    for k in series_timestamps((df.ripple_control)): ax[i].axvspan(k[0], k[1], 0, .05, color='red', alpha=0.5) # wants power but ripple control is on
    for k in series_timestamps((df.peak)): ax[i].axvspan(k[0], k[1], 0, .05, fc='none',hatch ='xx', ec='grey') # wants power but ripple control is on
    for k in series_timestamps((~df.ripple_control)): ax[i].axvspan(k[0], k[1], 0, .05, color='green', alpha=0.5) # wants power but ripple control is on
    network_legend = [Patch(facecolor='red', alpha=0.5 , label='Ripple Control'),
                      Patch(facecolor='green', alpha=0.5 ,  label='Normal Operation'),
                      Patch(facecolor='none', hatch='xx', ec='grey', label='Peak Demand')]


    legend1 = plt.legend(handles = network_legend,loc='upper center',title="Electricity Network", bbox_to_anchor=(0.2, -0.12), fancybox=True, shadow=False, ncol=3)
    legend2 = plt.legend(handles = operation_legend,loc='upper center',title="Operation", bbox_to_anchor=(0.7,-.12), fancybox=True, shadow=False, ncol=4)

    ax[i].add_artist(legend1)
    ax[i].add_artist(legend2)

    # add a colorbar for the price to the right of the plot
    fig.subplots_adjust(right=0.9)
    cbar_ax = fig.add_axes([0.92, 0.1, 0.02, 0.8])
    fig.colorbar(im, cax=cbar_ax)
    cbar_ax.set_ylabel('Price [$/kWh]', rotation=90, labelpad=5, fontsize=6)
    cbar_ax.yaxis.set_label_position('right')
    cbar_ax.yaxis.set_ticks_position('left')
    cbar_ax.yaxis.set_tick_params(pad=5)
    # cbar_ax.set_ylim(0, 0.2)
    cbar1_ax = fig.add_axes([0.97, 0.1, 0.02, 0.8])
    fig.colorbar(im2, cax=cbar1_ax)
    cbar1_ax.set_ylabel('kWh', rotation=90, labelpad=5, fontsize=6)
    cbar1_ax.yaxis.set_label_position('right')
    cbar1_ax.yaxis.set_ticks_position('left')
    cbar1_ax.yaxis.set_tick_params(pad=5)
    
    date_form = DateFormatter('%d %b\n %H:%M')
    ax[-1].xaxis.set_major_formatter(date_form)
    cbar_ax.yaxis.set_tick_params(labelsize=6)
    cbar1_ax.yaxis.set_tick_params(labelsize=6)
    ax[i].annotate('network', xy=(0, 0), xycoords='axes fraction',  xytext=(5, 10), textcoords='offset points', ha="left", va="top", fontsize=8)
    ax[i].annotate('operation', xy=(0, 0), xycoords='axes fraction',  xytext=(5, 28), textcoords='offset points', ha="left", va="top", fontsize=8)
    # add some whitespace to the bottom of the plot
    fig.subplots_adjust(bottom=0.25)
    fig.suptitle(title)
    return 
