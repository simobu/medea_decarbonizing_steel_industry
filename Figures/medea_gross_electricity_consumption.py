from gdx_import import initial_cap
from gdx_import import gdx_import
from pathlib import Path
from config import ROOT_DIR
from gdx_import_tableau import generation_filter
from gdx_import_tableau import storage_capacity
from gdx_import_tableau import trade_analysis
from gdx_import_tableau import prices

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
rd_sym = ['cost_system', 'CAPACITY', 'invest', 'decommission', 'gen', 'MAP_OUTPUTS', 'CAPACITY_STORAGE', 'storage_cap_neg_invest', 'storage_cap_invest', 'fuel_trade','balance', 'curtail'] #name of variables that should be imported from gdx output
technologies = ['Wind_Off', 'Wind_On', 'aec_100MW', 'battery', 'bio',
       'bio_boiler_chp', 'bio_chp', 'eboi_pth', 'h_2_cc_hi',
       'h_2_cc_hi_chp', 'h_2_fuel_cell', 'h_2_s_cavern', 'heatpump_pth',
       'hpa_pth', 'hw_tank', 'hyd_psp_day', 'hyd_psp_season',
       'hyd_psp_week', 'hyd_res_day', 'hyd_res_season', 'hyd_res_week',
       'pv', 'ror', 'soec_1MW']
generation_techs_el = ['Wind_Off', 'Wind_On', 'bio', 'h_2_cc_hi', 'pv', 'ror'] #
storage_techs = ['battery', 'h_2_s_cavern', 'hw_tank', 'hyd_psp_day',
       'hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season',
       'hyd_res_week']
hyd_storage_techs = ['hyd_psp_day','hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season','hyd_res_week']
bio_techs = ['bio','bio_boiler_chp', 'bio_chp']
h2_techs = ['h_2_cc_hi','h_2_cc_hi_chp']
######################################################
#initiate result dfs
results_installed_capacity = dict()
results_ann_gen_el = dict()
results_ann_gen_ht = dict()
results_ann_gen = dict()
results_stor_cap = dict()
results_h2_import = pd.DataFrame()#index=['AT','DE'])
results_ann_gen_h2 = pd.DataFrame()
results_prices = dict()
results_sys_cost = pd.DataFrame() #index=['Total System Cost [k€]'])
for ctry in ['AT','DE']:
    #results_installed_capacity[ctry] = pd.DataFrame(index=technologies)
    #results_stor_cap[ctry] = pd.DataFrame(index=storage_techs)

    #own dfs in dictionary for each scenario in each storyline
    for scenario in scenarios:
        for j in storyline:
            results_installed_capacity[ctry,str(scenario + j)] = pd.DataFrame(index=technologies)
            results_ann_gen_el[ctry,str(scenario + j)] = pd.DataFrame(index=technologies)
            results_ann_gen_ht[ctry,str(scenario + j)] = pd.DataFrame()
            results_stor_cap[ctry, str(scenario + j)] = pd.DataFrame(index=storage_techs)
            for f in ['el','h_2','ht']:
                if f!='ht':
                    results_prices[ctry,str(scenario + j),f] = pd.DataFrame(index=range(1,8761))


############### import results from excel ###############
# requires to do imports + define initial variables first
#import simple dataframes
path_excel_out = Path(ROOT_DIR + '/data/results/20230104')
results_sys_cost = pd.read_excel(path_excel_out / 'system_costs.xlsx', index_col=0)
results_h2_import = pd.read_excel(path_excel_out / 'h2_imports.xlsx', index_col=0)
results_ann_gen_h2 = pd.read_excel(path_excel_out / 'annual_h2_generation.xlsx', index_col=0)
inflows = pd.read_excel(path_excel_out / 'inflows.xlsx', index_col=0)
results_gross_gen = pd.read_excel(path_excel_out / 'gross_electricity_consumption.xlsx',index_col=0)
## import dictionaries
#define empty dictionaries
results_ann_gen_el = dict()
results_ann_gen_ht = dict()
results_installed_capacity = dict()
results_prices = dict()
results_stor_cap = dict()
#prepare scenario list to correctly access and write names + import data
scenario_list = []
for ctry in ['AT','DE']:
    for scenario in scenarios:
        for j in storyline:
            run_id = str(scenario+j)
            scenario_list.append(run_id)
    for i in scenario_list:
        results_ann_gen_el[ctry,i] = pd.read_excel(path_excel_out / str('annual_electricity_generation_' + ctry + '.xlsx'), sheet_name=i, index_col=0)
        results_ann_gen_ht[ctry,i] = pd.read_excel(path_excel_out / str('annual_heat_generation_' + ctry + '.xlsx'), sheet_name=i, index_col=0)
        results_installed_capacity[ctry,i] = pd.read_excel(path_excel_out / str('installed_capacities' + ctry + '.xlsx'), sheet_name=i, index_col=0)
        results_stor_cap[ctry,i] = pd.read_excel(path_excel_out / str('storage_capacities_' + ctry + '.xlsx'), sheet_name=i, index_col=0)
        for f in ['el', 'h_2']:
            results_prices[ctry,i,f] = pd.read_excel(path_excel_out / str(f + '_prices_' + ctry +'.xlsx'), sheet_name=i, index_col=0)


############### summarize annual generation #################

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

########################## gross energy consumption calculation #############
'''GEC = total annual generation - generation from storages (would otherwise be double counted)
 + inflows*0,9 (if ctry = AT; necessary as energy from inflows is actually newly generated with 90% efficiency)
 -  electricity exports (exports are positive, imports negative)
  + H2 imports/0.715'''
#import h2 import results + electricity exports
results_h2_imports = pd.DataFrame()
results_h2_imports = pd.read_excel(path_excel_out / 'h2_imports.xlsx',index_col=0)
results_exports = dict()
for ctry in ['AT','DE']:
    results_exports[ctry] = pd.read_excel(path_excel_out / 'exports.xlsx', sheet_name=ctry,index_col=0)
#prepare total gen df
#results_gross_gen = pd.DataFrame(columns = h2_price_list) # df for gross annual electricity consumption
#define x axis for plot
x = h2_price_list
#linestyles
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']

fig,axs = plt.subplots(1,2)
plotcount = 0
#fill plot
for ctry in ['AT','DE']:
    #third loop: select scenario
    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    if ctry == 'AT':
        axs[plotcount].set_ylim(130,155)
    else:
        axs[plotcount].set_ylim(1300,1550)
    axs[plotcount].set_title(str('Gross Electricity Consumption in ' + ctry),fontweight='bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('Energy [TWh]')
    #count to access index for linestyle and color
    count = 0
    for scenario in scenarios:
        #fourth loop
        for j in storyline:
            #calculation of gross electricity consumtion (see explanation above)
            #if ctry == 'AT':
            #    results_gross_gen.loc[str(ctry + scenario + j),:] = np.add(list(results_ann_gen_summary[ctry,str(scenario + j)].sum()/1000 - results_ann_gen_summary[ctry,str(scenario + j)].loc['battery',:]/1000\
            #        - results_ann_gen_summary[ctry,str(scenario + j)].loc['hydro_storage_techs',:]/1000\
            #        + inflows.iloc[0,0]/1000),\
            #        list(results_h2_imports.loc[str(ctry + scenario +j),:]/1000/0.715\
            #        - results_exports[ctry].loc[str(scenario+j),:]/1000))# /1000 --> convert GWh to TWh
            #else: #in DE no inflows into hydro storages are included in the model
            #    results_gross_gen.loc[str(ctry + scenario + j),:] = np.add(list(results_ann_gen_summary[ctry,str(scenario + j)].sum()/1000 - results_ann_gen_summary[ctry,str(scenario + j)].loc['battery',:]/1000\
            #        - results_ann_gen_summary[ctry,str(scenario + j)].loc['hydro_storage_techs',:]/1000),\
            #        list(results_h2_imports.loc[str(ctry + scenario +j),:]/1000/0.715\
            #        - results_exports[ctry].loc[str(scenario+j),:]/1000))# /1000 --> convert GWh to TWh
            y = list(results_gross_gen.loc[str(ctry + scenario + j),:])
            axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    axs[plotcount].legend(loc= 'best')
    plotcount = plotcount + 1

#to excel
results_gross_gen.to_excel(path_excel_out / 'gross_electricity_consumption.xlsx')
