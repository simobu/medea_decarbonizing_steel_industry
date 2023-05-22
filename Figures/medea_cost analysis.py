
from pathlib import Path
from config import ROOT_DIR
from operator import add
from gdx_import import gdx_import
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
#rd_sym = ['cost_system', 'CAPACITY', 'invest', 'decommission', 'gen', 'MAP_OUTPUTS', 'CAPACITY_STORAGE', 'storage_cap_neg_invest', 'storage_cap_invest', 'fuel_trade','balance', 'curtail'] #name of variables that should be imported from gdx output
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
el_storage_techs = ['battery','hyd_psp_day',
       'hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season',
       'hyd_res_week']
hyd_storage_techs = ['hyd_psp_day','hyd_psp_season', 'hyd_psp_week', 'hyd_res_day', 'hyd_res_season','hyd_res_week']
bio_techs = ['bio','bio_boiler_chp', 'bio_chp']
h2_techs = ['h_2_cc_hi','h_2_cc_hi_chp']

############### import results from excel ###############
# requires to do imports + define initial variables first
## define dictionaries and import path
path_excel_out = Path(ROOT_DIR + '/data/results/20230104')
results_cost_zonal = dict() #zonal costs in AT and DE
results_cost_summary = dict() #total system costs by cost type (invest, O&M,etc)
results_invest_summary = dict()
results_cost_summary_AT = dict()
results_cost_summary_DE = dict()

scenario_list = list()
for scenario in scenarios:
    for j in storyline:
        results_cost_summary[str(scenario + j)] = pd.DataFrame()
        scenario_list.append(str(scenario+j))
        results_cost_summary_AT[str(scenario + j)] = pd.DataFrame()
        results_cost_summary_DE[str(scenario + j)] = pd.DataFrame()
#import simple dataframes
results_sys_cost = pd.read_excel(path_excel_out / 'system_costs.xlsx', index_col=0) #total system ocsts
## import dictionaries
for ctry in ['AT','DE']:
    results_cost_zonal[ctry]=pd.read_excel(path_excel_out / str('cost_zonal_' + ctry + '.xlsx'),index_col=0)
for s in scenario_list:
    results_cost_summary[s] = pd.read_excel(path_excel_out / str('system_costs_detailed.xlsx'),sheet_name=s,index_col=0)
    results_cost_summary_AT[s] = pd.read_excel(path_excel_out / 'system_costs_AT_detailed.xlsx',sheet_name=s,index_col=0)
    results_cost_summary_DE[s] = pd.read_excel(path_excel_out / 'system_costs_DE_detailed.xlsx',sheet_name=s,index_col=0)
for j in storyline:
    results_invest_summary[str(j)] = pd.DataFrame()
    results_invest_summary[str(j)] = pd.read_excel(path_excel_out / 'invest_costs_differences_.xlsx',sheet_name=str(j),index_col=0)


############### system cost graph ##########
fig,ax = plt.subplots()
ax.set_xticks(h2_price_list)
ax.set_xlim(25,95)
ax.set_ylim(30,38)
ax.set_title('Total System Cost', fontweight = 'bold')
ax.set_xlabel('Hydrogen Import Price [EUR/MWh]')
ax.set_ylabel('Total System Cost [billion €]')
x = h2_price_list
#count to access index for linestyle and color
count = 0
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']
for scenario in scenarios:
    for j in storyline:
        #define name of  to be imported
        run_id = scenario + j
        print(run_id)
        y = list(results_sys_cost.loc[str(scenario +j),:]/1000000) #also convert to Mrd €
        ax.plot(x,y,
            color = linecolor[count],
            linestyle = linesty[count],
            label = labellist[count]
            )
        count = count + 1
ax.legend(loc='best')

########## zonal system cost graph ###########
############### system cost graph ##########
x = h2_price_list
#count to access index for linestyle and color
linesty = ['-','--',':','-','--',':']
linecolor = ['b','b','b','r','r','r']
labellist = ['el no constraints','el wind constraint','el wind + pv constraint','h2 no constraints','h2 wind constraint','h2 wind + pv constraint']

fig,axs = plt.subplots(1,2)
plotcount = 0
for ctry in ['AT','DE']:
    count = 0
    if ctry == 'AT':
        axs[plotcount].set_ylim(2.3,6.3)
    else:
        axs[plotcount].set_ylim(27,34)
    axs[plotcount].set_xticks(h2_price_list)
    axs[plotcount].set_xlim(25,95)
    axs[plotcount].set_title(str('System Costs in ' + ctry), fontweight = 'bold')
    axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
    axs[plotcount].set_ylabel('System Costs [billion €]')
    for scenario in scenarios:
        for j in storyline:
            #define name of  to be imported
            run_id = scenario + j
            print(run_id)
            y = list(results_cost_zonal[ctry].loc[str(scenario +j),:]/1000000) #convert to billion €
            axs[plotcount].plot(x,y,
                color = linecolor[count],
                linestyle = linesty[count],
                label = labellist[count]
                )
            count = count + 1
    axs[plotcount].legend(loc='best', fontsize=8)
    plotcount = plotcount +1



############# cost differences in entire system as one plot ############
"""one plot with 3 subplots that show the differences between cost types between the electricity
 and hydrogen scenarios"""

#calculate cost differences
cost_difference = dict()
cost_difference_percent = dict()
for j in storyline:
       cost_difference[j] = pd.DataFrame()
       #rename columns in h2 df so subtraction is possible
       col_names = list(results_cost_summary[str('el' + j)].columns)
       result_subtract = results_cost_summary[str('h_2' + j)]
       result_subtract.columns = col_names
       #subtract
       cost_difference[j] = results_cost_summary[str('el' + j)].subtract(result_subtract)
       cost_difference_percent[j] = pd.DataFrame(columns=cost_difference[j].columns)
       for i in cost_difference[j].columns:
              cost_difference_percent[j][i] = cost_difference[j][i]/cost_difference[j].loc['cost_system',i]

# plot
barWidth = 4
plot_technologies = h2_price_list
b1 = h2_price_list
#define labels and colors
labeldict = {'cost_invest':'Investment Costs','cost_om':'O & M costs','cost_inputs':'Fuel Costs (Biomass)','cost_stor_volume':'Additional Storage Capacity','cost_trade':'H2 Import Costs'}
colordict = {'cost_inputs':'green','cost_om':'orange','cost_invest':'royalblue','cost_trade':'sienna','cost_stor_volume':'grey'}#violet
fig,axs = plt.subplots(1,3)
count = 0
plotcount = 0
for j in storyline:
       #define/reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = (max(cost_difference[j].loc['cost_system']) + abs(min(cost_difference[j].loc['cost_trade'])))/1000
       column_sum = 0
       for cost_type in labeldict:
              br_plot = b1  #defines x axis locations for bars
              y = list(cost_difference[j].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # created list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r]
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colordict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = cost_difference[j].loc['cost_system',str('el' + j + str(i))]/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-1300,2100)
       axs[plotcount].set_yticks([-1200,-800,-400,0,400,800,1200,1600,2000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')

       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str('System Cost Differences between Electricity and Hydrogen Scenarios by Cost Types \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1


################ invest cost differences of entire system ###############
'''plot differences in investment costs between electricity and hydrogen scenarios in a bar plot
positive value indicate higher investment costs in electricity scenario, 
negative values indicate higher investment costs in hydrogen scenario
black bars in plot additionally indicate aggregated investment cost differences between the 
respective el and H2 scenarios'''
#
barWidth = 4

#define x axis names
plot_technologies = h2_price_list
#list with labels
b1 = h2_price_list
#define labels and colors in plot
colors_dict = {'Wind_On':'b','pv':'orange','bio_techs':'g','heatpump_pth':'magenta','eboi_pth':'darkviolet','aec_100MW':'cyan','h_2_s_cavern':'gold','h_2_cc_hi':'red','storage_techs':'grey'}
labeldict = {'Wind_On':'Onshore Wind','pv':'PV','bio_techs':'Biomass','heatpump_pth':'Heatpumps','eboi_pth':'Electric Boilers','aec_100MW':'Electrolyzers','h_2_s_cavern':'H2 Storage','h_2_cc_hi':'H2 Power Plants','storage_techs':'Electricity Storage \n Output Capacity'}
#start plotting
fig,axs = plt.subplots(1,3)
plotcount = 0
count = 0
for j in storyline:
       #reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = max(results_invest_summary[str(j)].sum(axis = 0)/1000) + abs(min(results_invest_summary[str(j)].sum(axis = 0)/1000))
       column_sum = 0
       for cost_type in results_invest_summary[str(j)].index:
              br_plot = b1  #defines x axis locations for bars
              y = list(results_invest_summary[str(j)].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # created list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r]
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colors_dict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = results_invest_summary[str(j)][i].sum()/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-350,1100)
       axs[plotcount].set_yticks([-200,0,200,400,600,800,1000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
           axs[plotcount].legend(prop={'size':7})
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str(' \n Invest Cost Differences between Electricity and Hydrogen Scenarios \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1



########## invest cost differences by country #######
'''Script does not yet exist: requires calculate incest costs by country and summarize them into 
technology categories
invest_results per country however already exist as excel files'''
#define data structure
invest_cost_difference_AT = dict()
invest_cost_difference_DE = dict()
#import from excel
for j in storyline:
    invest_cost_difference_AT[j] = pd.read_excel(path_excel_out / 'invest_cost_differences_AT.xlsx', sheet_name=j,index_col=0)
    invest_cost_difference_DE[j] = pd.read_excel(path_excel_out / 'invest_cost_differences_DE.xlsx', sheet_name=j,index_col=0)

### plot AT ###
barWidth = 4
#define x axis names
plot_technologies = h2_price_list
#list with labels
b1 = h2_price_list
#define labels and colors in plot
colors_dict = {'Wind_On':'b','pv':'orange','bio_techs':'g','heatpump_pth':'magenta','eboi_pth':'darkviolet','aec_100MW':'cyan','h_2_s_cavern':'gold','h_2_cc_hi':'red','storage_techs':'grey'}
labeldict = {'Wind_On':'Onshore Wind','pv':'PV','bio_techs':'Biomass','heatpump_pth':'Heatpumps','eboi_pth':'Electric Boilers','aec_100MW':'Electrolyzers','h_2_s_cavern':'H2 Storage','h_2_cc_hi':'H2 Power Plants','storage_techs':'Electricity Storage \n Output Capacity'}
#start plotting
fig,axs = plt.subplots(1,3)
plotcount = 0
count = 0
for j in storyline:
       #reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = max(invest_cost_difference_AT[str(j)].sum(axis = 0)/1000) + abs(min(invest_cost_difference_AT[str(j)].sum(axis = 0)/1000))
       column_sum = 0
       for cost_type in invest_cost_difference_AT[str(j)].index:
              br_plot = b1  #defines x axis locations for bars
              y = list(invest_cost_difference_AT[str(j)].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # created list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r]
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colors_dict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = invest_cost_difference_AT[str(j)][i].sum()/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-350,1100)
       axs[plotcount].set_yticks([-200,0,200,400,600,800,1000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
           axs[plotcount].legend(prop={'size':7})
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str(' \n Invest Cost Differences between Electricity and Hydrogen Scenarios in AT \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1


### plot DE ###
barWidth = 4
#define x axis names
plot_technologies = h2_price_list
#list with labels
b1 = h2_price_list
#define labels and colors in plot
colors_dict = {'Wind_On':'b','pv':'orange','bio_techs':'g','heatpump_pth':'magenta','eboi_pth':'darkviolet','aec_100MW':'cyan','h_2_s_cavern':'gold','h_2_cc_hi':'red','storage_techs':'grey'}
labeldict = {'Wind_On':'Onshore Wind','pv':'PV','bio_techs':'Biomass','heatpump_pth':'Heatpumps','eboi_pth':'Electric Boilers','aec_100MW':'Electrolyzers','h_2_s_cavern':'H2 Storage','h_2_cc_hi':'H2 Power Plants','storage_techs':'Electricity Storage \n Output Capacity'}
#start plotting
fig,axs = plt.subplots(1,3)
plotcount = 0
count = 0
for j in storyline:
       #reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = max(invest_cost_difference_DE[str(j)].sum(axis = 0)/1000) + abs(min(invest_cost_difference_DE[str(j)].sum(axis = 0)/1000))
       column_sum = 0
       for cost_type in invest_cost_difference_DE[str(j)].index:
              br_plot = b1  #defines x axis locations for bars
              y = list(invest_cost_difference_DE[str(j)].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # created list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r]
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colors_dict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = invest_cost_difference_DE[str(j)][i].sum()/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-350,1100)
       axs[plotcount].set_yticks([-200,0,200,400,600,800,1000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')
       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
           axs[plotcount].legend(prop={'size':7})
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str(' \n Invest Cost Differences between Electricity and Hydrogen Scenarios in DE \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1000),ha='left')
           axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1


################ zonal costs by cost type ########
'''costs differences by octs type (investment, O&M, imports, etc)'''
#prepare data
##### calculate cost differences
cost_difference_AT = dict()
cost_difference_DE = dict()
for j in storyline:
       cost_difference_AT[j] = pd.DataFrame()
       cost_difference_DE[j] = pd.DataFrame()
       # subtraction
       cost_difference_AT[j] = np.subtract(results_cost_summary_AT[str('el' + j)],results_cost_summary_AT[str('h_2' + j)])
       cost_difference_DE[j] = np.subtract(results_cost_summary_DE[str('el' + j)],results_cost_summary_DE[str('h_2' + j)])


############# cost differences for AT ############
"""one plot with 3 subplots that show the differences between cost types between the electricit yand hydrogen scenarios"""
# set width of bar
barWidth = 4
plot_technologies = h2_price_list
b1 = h2_price_list
labeldict = {'cost_invest':'Investment Costs','cost_om':'O & M costs','cost_inputs':'Fuel Costs (Biomass)','cost_stor_volume':'Additional Storage Capacity','cost_trade':'H2 Import Costs'}
colordict = {'cost_inputs':'green','cost_om':'orange','cost_invest':'royalblue','cost_trade':'sienna','cost_stor_volume':'grey'}#violet

fig,axs = plt.subplots(1,3)
count = 0
plotcount = 0
for j in storyline:
       #define/reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = (max(cost_difference_AT[j].loc['cost_zonal']) + abs(min(cost_difference_AT[j].loc['cost_trade'])))/1000
       column_sum = 0
       for cost_type in labeldict:
              br_plot = b1  #defines x axis locations for bars
              y = list(cost_difference_AT[j].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # creates list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r] #add negative bottom values in case there are more than 2 negative values
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colordict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = cost_difference_AT[j].loc['cost_zonal',str('el' + j + str(i))]/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-1300,2100)
       axs[plotcount].set_yticks([-1200,-800,-400,0,400,800,1200,1600,2000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')

       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str('System Cost Differences between Electricity and Hydrogen Scenarios by Cost Types in AT \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1

############# cost differences for DE ############
"""one plot with 3 subplots that show the differences between cost types between the electricit yand hydrogen scenarios"""
# set width of bar
barWidth = 4
plot_technologies = h2_price_list
b1 = h2_price_list
labeldict = {'cost_invest':'Investment Costs','cost_om':'O & M costs','cost_inputs':'Fuel Costs (Biomass)','cost_stor_volume':'Additional Storage Capacity','cost_trade':'H2 Import Costs'}
colordict = {'cost_inputs':'green','cost_om':'orange','cost_invest':'royalblue','cost_trade':'sienna','cost_stor_volume':'grey'}#violet

fig,axs = plt.subplots(1,3)
count = 0
plotcount = 0
for j in storyline:
       #define/reset intermediate values
       bottom_value = list([0]*len(plot_technologies))
       bottom_neg_value = list([0]*len(plot_technologies))
       bottom_save = list([0]*len(plot_technologies))
       minimum = 0
       maximum = (max(cost_difference_DE[j].loc['cost_zonal']) + abs(min(cost_difference_DE[j].loc['cost_trade'])))/1000
       column_sum = 0
       for cost_type in labeldict:
              br_plot = b1  #defines x axis locations for bars
              y = list(cost_difference_DE[j].loc[cost_type,:]/1000)#access values for one cost type and convert to million€
              #update min values
              if minimum > min(y):
                  minimum = min(y)
              ##### define new bottom values ########
              #check if a value is negative ---> requires 0 or negative value as a bottom
              res = [ind for ind in range(len(y)) if y[ind] < 0] # created list with indeces of negative numbers
              if len(res) > 0:# if there are negative values
                     #set bottom value for the negative values
                     for r in res:
                         #save original bottom values
                         bottom_save[r] = bottom_value[r]
                         bottom_value[r] = bottom_neg_value[r]
                         #set new negative bottom value in case there is another negative value in the column
                         bottom_neg_value[r] = bottom_neg_value[r] + y[r]
              #plot
              axs[plotcount].bar(br_plot,y,width=barWidth,bottom=bottom_value,label=labeldict[cost_type],color=colordict[cost_type])
              #write new bottom values for next plot iteration
              bottom_value = list(map(add,bottom_value, y)) #sum up previous bars to get the bottom value for the next plot
              #restore bottom value if they were changed
              if len(res)>0:
                     for r in res:
                            bottom_value[r] = bottom_save[r]
              #print(bottom_value)
       #include black dashed line for 0 line
       axs[plotcount].plot([25,95],[0,0],'k--')
       #include small black bar for sum
       for i in h2_price_list:
           y_plot = cost_difference_DE[j].loc['cost_zonal',str('el' + j + str(i))]/1000
           axs[plotcount].plot([i-barWidth/2,i+barWidth/2],[y_plot,y_plot],'k')
       # add count and write labels
       count = count + 1
       axs[plotcount].set_ylim(-1300,2100)
       axs[plotcount].set_yticks([-1200,-800,-400,0,400,800,1200,1600,2000])
       axs[plotcount].set_xticks(plot_technologies)
       axs[plotcount].set_xlabel('Hydrogen Import Price [EUR/MWh]')

       if j == '_':
           axs[plotcount].set_title(str('No Constraints'),fontweight='bold')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           axs[plotcount].annotate('a)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].set_ylabel('Cost Difference [million €]')
       elif j == '_wind_constraint_':
           axs[plotcount].set_title(str('System Cost Differences between Electricity and Hydrogen Scenarios by Cost Types in DE \n \n Wind Constraint'),fontweight='bold')
           axs[plotcount].annotate('b)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       else:
           axs[plotcount].set_title(str('Wind and PV Constraint'),fontweight='bold')
           axs[plotcount].annotate('c)',fontweight='bold',xy=(23,1900),ha='left')
           axs[plotcount].legend(loc='lower right',prop={'size':7})
           #axs[plotcount].legend(prop={'size':7})
       plotcount = plotcount + 1







############### Documentation: calculating country specific invest cost differences ############
'''writes excel files'''
invest_summary_AT = dict()
invest_summary_DE = dict()
invest_difference_AT = dict()
invest_difference_DE = dict()
results_CAPITALCOST = pd.DataFrame()
#import invest results
for s in scenario_list:
    invest_summary_AT[s] = pd.read_excel(path_excel_out / 'invest_results_AT.xlsx',sheet_name=s,index_col=0)
    invest_summary_DE[s] = pd.read_excel(path_excel_out / 'invest_results_DE.xlsx',sheet_name=s,index_col=0)
# import invest costs (CAPITALCOSTS)
rd_sym = ['CAPITALCOST']
run_id = 'el_90' #name of iteration
gdx_name = 'medea_out_' + run_id + '.gdx'
results = gdx_import(rd_sym,root_dir,gdx_name)
for i in h2_price_list:
    results_CAPITALCOST[i] = list(results['CAPITALCOST'].iloc[:,2])
    results_CAPITALCOST.index = list(results['CAPITALCOST']['t_1'])
# calculate invest difference
#subtract h2 scenarios from el scenarios
for ctry in ['AT','DE']:
    for j in storyline:
        invest_difference_AT[j] = np.subtract(invest_summary_AT[str('el'+j)],invest_summary_AT[str('h_2'+j)])
        invest_difference_DE[j] = np.subtract(invest_summary_DE[str('el'+j)],invest_summary_DE[str('h_2'+j)])
#calculate invest cost differences
for j in storyline:
    invest_cost_difference_AT[j] = np.multiply(invest_difference_AT[j],results_CAPITALCOST[:24])
    invest_cost_difference_DE[j] = np.multiply(invest_difference_DE[j],results_CAPITALCOST[:24])
    #combine storage technologies
    invest_cost_difference_AT[j].loc['storage_techs',:] = invest_cost_difference_AT[j].loc[el_storage_techs].sum()
    invest_cost_difference_AT[j] = invest_cost_difference_AT[j].drop(el_storage_techs)
    invest_cost_difference_DE[j].loc['storage_techs',:] = invest_cost_difference_DE[j].loc[el_storage_techs].sum()
    invest_cost_difference_DE[j] = invest_cost_difference_DE[j].drop(el_storage_techs)
    #combine biomass technologies
    invest_cost_difference_AT[j].loc['bio_techs',:] = invest_cost_difference_AT[j].loc[bio_techs].sum()
    invest_cost_difference_AT[j] = invest_cost_difference_AT[j].drop(bio_techs)
    invest_cost_difference_DE[j].loc['bio_techs',:] = invest_cost_difference_DE[j].loc[bio_techs].sum()
    invest_cost_difference_DE[j] = invest_cost_difference_DE[j].drop(bio_techs)
    #remove rows with only zeros
    invest_cost_difference_AT[j] = invest_cost_difference_AT[j].loc[(invest_cost_difference_AT[j]!=0).any(axis=1)]
    invest_cost_difference_DE[j] = invest_cost_difference_DE[j].loc[(invest_cost_difference_DE[j]!=0).any(axis=1)]

#export to excel
with pd.ExcelWriter(path_excel_out / 'invest_cost_differences_AT.xlsx') as writer:
    invest_cost_difference_AT[storyline[0]].to_excel(writer, sheet_name= storyline[0])
    invest_cost_difference_AT[storyline[1]].to_excel(writer, sheet_name= storyline[1])
    invest_cost_difference_AT[storyline[2]].to_excel(writer, sheet_name= storyline[2])
with pd.ExcelWriter(path_excel_out / 'invest_cost_differences_DE.xlsx') as writer:
    invest_cost_difference_DE[storyline[0]].to_excel(writer, sheet_name= storyline[0])
    invest_cost_difference_DE[storyline[1]].to_excel(writer, sheet_name= storyline[1])
    invest_cost_difference_DE[storyline[2]].to_excel(writer, sheet_name= storyline[2])







############### documentation: creating system_costs_AT_detailed.xlsx ###########
'''writes excel files'''
#import
rd_sym = ['cost_zonal', 'cost_inputs','cost_om','cost_invest','cost_grid','cost_nse','cost_trade','cost_stor_volume'] #name of variables that should be imported from gdx output
results_cost_summary_AT = dict()
results_cost_summary_DE = dict()
for scenario in scenarios:
       for j in storyline:
              results_cost_summary_AT[str(scenario + j)] = pd.DataFrame()
              results_cost_summary_DE[str(scenario + j)] = pd.DataFrame()
#read data from gdx files
for scenario in scenarios:
       for j in storyline:
              count_list = 0
              for i in h2_price_list:
                     run_id = scenario + j + str(i) #name of iteration
                     gdx_name = 'medea_out_' + run_id + '.gdx'
                     #import gdx file
                     results = gdx_import(rd_sym,root_dir,gdx_name)
                     #write zonal system costs
                     results_cost_summary_AT[str(scenario + j)].loc['cost_zonal',run_id] = float(results['cost_zonal'].loc[(results['cost_zonal']['z_0']=='AT'),'level'])
                     results_cost_summary_DE[str(scenario + j)].loc['cost_zonal',run_id] = float(results['cost_zonal'].loc[(results['cost_zonal']['z_0']=='DE'),'level'])
                     #write individual components (each a sum of all technologies)
                     for cost_type in rd_sym:
                         if cost_type == 'cost_zonal': continue #skips the entry 'cost_system'
                         results_cost_summary_AT[str(scenario + j)].loc[cost_type,run_id] = float(results[cost_type].loc[(results[cost_type]['z_0']=='AT'),'level'].sum())
                         results_cost_summary_DE[str(scenario + j)].loc[cost_type,run_id] = float(results[cost_type].loc[(results[cost_type]['z_0']=='DE'),'level'].sum())
                     print(run_id + ' completed')

#################### export to excel #########
path_excel_out = Path(ROOT_DIR + '/data/results/20230104')
#create list with all scenario names
scenario_list = list()
for scenario in scenarios:
    for j in storyline:
        run_id = str(scenario+j)
        scenario_list.append(run_id)
###### results_costs ########### (unit: k€)
# annual electricity generation into excel
with pd.ExcelWriter(path_excel_out / str('system_costs_AT_detailed.xlsx')) as writer:
    results_cost_summary_AT[scenario_list[0]].to_excel(writer, sheet_name= scenario_list[0])
    results_cost_summary_AT[scenario_list[1]].to_excel(writer, sheet_name= scenario_list[1])
    results_cost_summary_AT[scenario_list[2]].to_excel(writer, sheet_name= scenario_list[2])
    results_cost_summary_AT[scenario_list[3]].to_excel(writer, sheet_name= scenario_list[3])
    results_cost_summary_AT[scenario_list[4]].to_excel(writer, sheet_name= scenario_list[4])
    results_cost_summary_AT[scenario_list[5]].to_excel(writer, sheet_name= scenario_list[5])
with pd.ExcelWriter(path_excel_out / str('system_costs_DE_detailed.xlsx')) as writer:
    results_cost_summary_DE[scenario_list[0]].to_excel(writer, sheet_name= scenario_list[0])
    results_cost_summary_DE[scenario_list[1]].to_excel(writer, sheet_name= scenario_list[1])
    results_cost_summary_DE[scenario_list[2]].to_excel(writer, sheet_name= scenario_list[2])
    results_cost_summary_DE[scenario_list[3]].to_excel(writer, sheet_name= scenario_list[3])
    results_cost_summary_DE[scenario_list[4]].to_excel(writer, sheet_name= scenario_list[4])
    results_cost_summary_DE[scenario_list[5]].to_excel(writer, sheet_name= scenario_list[5])

