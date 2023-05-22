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
root_dir = Path(ROOT_DIR + '/opt') #location of output gdx
#output path
path_out = Path(ROOT_DIR + '/data/results')
#which variables and parameters should be read from solution
generation_techs_el = ['Wind_Off', 'Wind_On', 'bio', 'h_2_cc_hi', 'pv', 'ror'] #
storage_techs = ['battery', 'h_2_s_cavern', 'hw_tank', 'hyd_psp_day',
       'hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season',
       'hyd_res_week']
hyd_storage_techs = ['hyd_psp_day','hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season','hyd_res_week']
bio_techs = ['bio','bio_boiler_chp', 'bio_chp']
h2_techs = ['h_2_cc_hi','h_2_cc_hi_chp']
flexible_gen_techs = ['battery','bio_techs','h2_techs','hydro_storage_techs']
#### import relevant results from excel
path_excel_out = Path(ROOT_DIR + '/data/results/20230104')
results_ann_gen_el = dict()
results_use_el = dict()
demands = dict()
exports = dict()
scenario_list = []
for ctry in ['AT','DE']:
    exports[ctry] = pd.read_excel(path_excel_out / 'exports.xlsx', sheet_name=ctry, index_col=0) #exports are defined positive
    demands[ctry] = pd.read_excel(path_excel_out / 'demands.xlsx',sheet_name=ctry)
    for scenario in scenarios:
        for j in storyline:
            run_id = str(scenario+j)
            scenario_list.append(run_id)
    for i in scenario_list:
        results_ann_gen_el[ctry,i] = pd.read_excel(path_excel_out / str('annual_electricity_generation_' + ctry + '.xlsx'), sheet_name=i, index_col=0)
        results_use_el[ctry,i] = pd.read_excel(path_excel_out / str('electricity_use_' + ctry + '.xlsx'), sheet_name=i, index_col=0)


#summarize annual generation data
results_ann_gen_summary = dict()
for ctry in ['AT','DE']:
    for scenario in scenarios:
        for j in storyline:
            #fill nan values with zeros
            results_ann_gen_el[ctry,str(scenario + j)] = results_ann_gen_el[ctry,str(scenario + j)].fillna(0)

            #initiate generation summary df
            results_ann_gen_summary[ctry,str(scenario + j)] = pd.DataFrame(columns = h2_price_list)
            results_ann_gen_summary[ctry,str(scenario + j)] = results_ann_gen_el[ctry,str(scenario + j)]
            #summarize annual electricity generation for hyd_storages, bio techs and h2 power plants
            #summarize bio technologies
            results_ann_gen_summary[ctry,str(scenario + j)].loc['bio_techs'] = results_ann_gen_summary[ctry,str(scenario+j)].loc[bio_techs].sum()
            results_ann_gen_summary[ctry,str(scenario + j)] = results_ann_gen_summary[ctry,str(scenario + j)].drop(bio_techs)
            #hydro storage technologies
            results_ann_gen_summary[ctry,str(scenario + j)].loc['hydro_storage_techs'] = results_ann_gen_summary[ctry,str(scenario+j)].loc[hyd_storage_techs].sum()
            results_ann_gen_summary[ctry,str(scenario + j)] = results_ann_gen_summary[ctry,str(scenario + j)].drop(hyd_storage_techs)
            #H2 Power Plants
            results_ann_gen_summary[ctry,str(scenario + j)].loc['H2_techs'] = results_ann_gen_summary[ctry,str(scenario+j)].loc[h2_techs].sum()
            results_ann_gen_summary[ctry,str(scenario + j)] = results_ann_gen_summary[ctry,str(scenario + j)].drop(h2_techs)
            #drop rows with only zeros
            results_ann_gen_summary[ctry,str(scenario + j)] = results_ann_gen_summary[ctry,str(scenario + j)].loc[(results_ann_gen_summary[ctry,str(scenario+j)]!=0).any(axis=1)]

#calculate electricity consumption (not necessary):
'''consumption = demand + P2H use + Electrolysis use + net imports (if country has net imports)'''
elec_consume = dict()
for ctry in ['AT','DE']:
    elec_consume[ctry] = pd.DataFrame(index=scenario_list[0:6],columns=h2_price_list)
    #add demand data
    elec_consume[ctry].iloc[0:3,:] = demands[ctry].iloc[0,1]
    elec_consume[ctry].iloc[3:6,:] = demands[ctry].iloc[1,1]
    #add imports
    ex_intermediate = exports[ctry]
    ex_intermediate[ex_intermediate > 0] = 0 #select only imports (negative values)
    elec_consume[ctry] = np.subtract(elec_consume[ctry],ex_intermediate) #add imports (i.e. subtract as they are negative
    #add P2H and electrolysis values
    for s in scenario_list[0:6]:
        elec_consume[ctry].loc[s,:] = np.add(elec_consume[ctry].loc[s,:],results_use_el[ctry,s].loc['P2Heat',:]+results_use_el[ctry,s].loc['Electrolysis',:])


############# annual flexible electricity generation (one plot)################
"""i.e. electricity generation from hydro storages, batteries, biomass and h2
in relation to total domestic electricity generation
AT and DE in one plot """

x = h2_price_list
#linestyles
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']

fig,axs = plt.subplots(1,2)
plotcount = 0
for ctry in ['AT','DE']:

    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    #axs[plotcount].set_ylim(15,35)
    #if ctry == 'DE':
    #    ax.set_ylim(18,25)
    axs[plotcount].set_title(str('Flexible Electricity Generation in ' + ctry),fontweight='bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('Share of Total Generation [%]')
    #count to access index for linestyle and color
    count = 0
    for scenario in scenarios:
        #fourth loop
        for j in storyline:
            #add all flexible generation techs (via the long way as we dont know which flexible technologies are used)
            y = list([0]*7)
            if 'bio_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = list(results_ann_gen_summary[ctry, str(scenario + j)].loc['bio_techs']/1000)
            if 'H2_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['H2_techs']/1000))
            if 'hydro_storage_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['hydro_storage_techs']/1000))
            if 'battery' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['battery']/1000))
            y = y/(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000)*100
            #y = y/np.subtract(list(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage']/1000))*100
            axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    axs[plotcount].legend(loc= 'best')
    plotcount = plotcount +1

############# annual flexible electricity generation (multiple plots)################
"""i.e. electricity generation from hydro storages, batteries, biomass and h2
in relation to total domestic electricity generation. One plot for per country """
x = h2_price_list
#linestyles
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
#second loop: country
for ctry in ['AT','DE']:

    fig,ax = plt.subplots()
    ax.set_xticks(h2_price_list)
    ax.set_xlim(25,95)
    #ax.set_ylim(18,25) #limits for DE plot
    ax.set_title(str('Flexible Electricity Generation in ' + ctry),fontweight='bold')
    ax.set_xlabel('Hydrogen Import Price [EUR/MWh]')
    ax.set_ylabel('Share of Total Generation [%]')
    count = 0
    for scenario in scenarios:
        #fourth loop
        for j in storyline:
            #add all flexible generation techs (via the long way as we dont know which flexible technologies are used)
            y = list([0]*7)
            if 'bio_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = list(results_ann_gen_summary[ctry, str(scenario + j)].loc['bio_techs']/1000)
            if 'H2_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['H2_techs']/1000))
            if 'hydro_storage_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['hydro_storage_techs']/1000))
            if 'battery' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y = np.add(y,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['battery']/1000))
            y = y/(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000)*100
            #y = y/np.subtract(list(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage']/1000))*100
            ax.plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    ax.legend(loc= 'best')





############# annual flexible electricity use (multiple plots) ################
"""i.e. flexible electricity consumption (storages and electrolysis)
as a share of electricity generation (definition see above). Individual plots for DE and AT"""

x = h2_price_list
#linestyles
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
#second loop: country
for ctry in ['AT','DE']:

    fig,ax = plt.subplots()
    ax.set_xticks(h2_price_list)
    ax.set_xlim(25,95)
    #ax.set_ylim(7,63)
    ax.set_ylim(36,47)
    #if ctry == 'DE':
    #    ax.set_ylim(17,45)
    ax.set_title(str('Flexible Electricity Use in ' + ctry),fontweight='bold')
    ax.set_xlabel('Hydrogen Import Price [EUR/MWh]')
    ax.set_ylabel('Share of Total Generation [%]')
    #count to access index for linestyle and color
    count = 0
    for scenario in scenarios:
        #fourth loop
        for j in storyline:
            #add all flexible generation techs (via the long way as we dont know which flexible technologies are used)
            y = np.add(list(results_use_el[ctry, str(scenario + j)].loc['Electrolysis',:]/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage',:]/1000))
            y = y/(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000)*100
            #y = y/np.subtract(list(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage']/1000))*100
            ax.plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    ax.legend(loc= 'best')


############# annual flexible electricity generation + use ################
"""i.e. electricity generation from hydro storages, batteries, biomass and h2
proportional generation: flexibly generated electricity/overall generated electricity
overall generated electricity: all generation"""

x = h2_price_list
#linestyles
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
fig,axs = plt.subplots(1,2)
plotcount = 0
#second loop: country
for ctry in ['AT','DE']:
    #third loop: select scenario

    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    axs[plotcount].set_ylim(45,70)
    #if ctry == 'DE':
    #    ax.set_ylim(18,25)
    axs[plotcount].set_title(str('Electricity System Flexibility in ' + ctry),fontweight='bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('Share of Total Generation [%]')
    #count to access index for linestyle and color
    count = 0
    for scenario in scenarios:
        #fourth loop
        for j in storyline:
            #add all flexible generation techs (via the long way as we dont know which flexible technologies are used)
            y1 = list([0]*7)
            if 'bio_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y1 = list(results_ann_gen_summary[ctry, str(scenario + j)].loc['bio_techs']/1000)
            if 'H2_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y1 = np.add(y1,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['H2_techs']/1000))
            if 'hydro_storage_techs' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y1 = np.add(y1,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['hydro_storage_techs']/1000))
            if 'battery' in results_ann_gen_summary[ctry, str(scenario + j)].index:
                y1 = np.add(y1,list(results_ann_gen_summary[ctry, str(scenario + j)].loc['battery']/1000))
            y1 = y1/(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000)*100
            y2 = np.add(list(results_use_el[ctry, str(scenario + j)].loc['Electrolysis',:]/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage',:]/1000))
            y2 = y2/(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000)*100
            y = y1+y2
            #y = y/np.subtract(list(results_ann_gen_summary[ctry, str(scenario + j)].sum()/1000),list(results_use_el[ctry, str(scenario + j)].loc['Storage']/1000))*100
            axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    axs[plotcount].legend(loc= 'center right')
    plotcount = plotcount + 1
