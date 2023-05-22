from pathlib import Path
from config import ROOT_DIR

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#define necessary information
#define possible h2 prices
h2_price_list = list(range(30,100,10))
#define scenario
scenarios = ['el','h_2']
storyline = ['_','_wind_constraint_','_windpv_constraint_']
#input path
path_excel_out = Path(ROOT_DIR + '/data/results/20230104') #location of excel files
#output path
path_out = Path(ROOT_DIR + '/data/results')

#import data from excel files
results_h2_import = pd.read_excel(path_excel_out / 'h2_imports.xlsx', index_col=0)
results_ann_gen_h2 = pd.read_excel(path_excel_out / 'annual_h2_generation.xlsx', index_col=0)

############ annual H2 production 2 plots in one figure ###########
'''one plot for AT and one for DE in one Figure'''
#prepare line plot
#x-values --> h2 import price
x = h2_price_list
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
plotcount = 0
fig,axs = plt.subplots(1,2)
for ctry in ['AT','DE']: #create one plot per country
    h2_plot = pd.DataFrame() #empty plot df
    count = 0 #count to access linestyle and color
    #prepare plotting
    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    if ctry == 'AT':
        axs[plotcount].set_ylim(0,34)
    else:
        axs[plotcount].set_ylim(0,340)
    axs[plotcount].set_title(str('Domestic Hydrogen Production in ' + ctry), fontweight = 'bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('Hydrogen Production [TWh]')
    #access only row relevant for each country
    h2_plot = results_ann_gen_h2.loc[(results_ann_gen_h2.index.str.contains(ctry))]
    for row in list(range(len(h2_plot.index))): #each row in df is one line in plot
        #define row name
        y = list(h2_plot.iloc[row,:]/1000)
        #plot
        axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                #label = list(h2_plot.index)[row].strip(ctry)
                label = labellist[count]
                )
        count = count + 1
    if ctry == 'DE':
        axs[plotcount].legend(loc = 'lower right')
    plotcount = plotcount +1


############ annual H2 imports 2 plots in one figure ###########
'''one plot for AT and one for DE in one Figure'''
#prepare line plot
#x-values --> h2 import price
x = h2_price_list
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
plotcount = 0
fig,axs = plt.subplots(1,2)
for ctry in ['AT','DE']: #create one plot per country
    h2_plot = pd.DataFrame() #empty plot df
    count = 0 #count to access linestyle and color
    #prepare plotting
    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    if ctry == 'AT':
        axs[plotcount].set_ylim(0,180)
    else:
        axs[plotcount].set_ylim(0,180)
    axs[plotcount].set_title(str('Hydrogen Imports into ' + ctry), fontweight = 'bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('Hydrogen Imports [TWh]')
    #access only row relevant for each country
    h2_plot = results_h2_import.loc[(results_h2_import.index.str.contains(ctry))]
    for row in list(range(len(h2_plot.index))): #each row in df is one line in plot
        #define row name
        y = list(h2_plot.iloc[row,:]/1000)
        #plot
        axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                #label = list(h2_plot.index)[row].strip(ctry)
                label = labellist[count]
                )
        count = count + 1
    if ctry == 'DE':#places legend in DE plot
        axs[plotcount].legend(loc = 'best')
    plotcount = plotcount +1

###### hourly h2 analysis ##########
'''Figure that shows the average hourly H2 production of all scenarios. One plot for AT and one plot for DE'''
#import excel data
hourly_h2 = dict()
for scenario in scenarios:
    for j in storyline:
        for ctry in ['AT','DE']:
            hourly_h2[ctry,str(scenario+j)] = pd.read_excel(path_excel_out / str('hourly_average_h2_gen_'+ctry+'.xlsx'), sheet_name= str(scenario+j), index_col=0)
#simple line plot with the average hourly H2 production in one day in all scenarios
fig,axs = plt.subplots(1,2)
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
x = list(range(1,25))
plotcount = 0
for ctry in ['AT','DE']:
    count = 0
    axs[plotcount].set_xticks(range(0,25,3))
    axs[plotcount].set_xlim(0,24)
    axs[plotcount].set_title(str('Average Hourly Hydrogen Production in ' + ctry), fontweight = 'bold')
    axs[plotcount].set_xlabel('Hour of the Day')
    axs[plotcount].set_ylabel('Average Production [GW]')
    for scenario in scenarios:
        for j in storyline:
            run_id = scenario + j
            for i in h2_price_list:
                y = list(hourly_h2[ctry,str(scenario +j)][i])
                axs[plotcount].plot(x,y,
                    color = linecolor[count],
                    linestyle = linesty[count],
                    label = labellist[count] if i == 30 else "_nolegend_" #if clause removes duplicates in legend
                )
            count = count + 1
    if ctry == 'DE':#places legend in DE plot
        axs[plotcount].legend(loc = 'best', fontsize= 7)
    plotcount = plotcount + 1

