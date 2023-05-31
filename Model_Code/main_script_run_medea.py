'''This script runs the power system model with all scenarios defined in the study "decarbonizing the
steel industry: how does a 100 % renewable powered steel production influence electricity system
structure and costs in Austriaand Germany?
--> The power system model medea must be preconfigured for this script to function. The "compile_symbols.py"
function of the power system model medea was altered and must be replaced with the function provided in this
repository. Data is stored in the local directory defined in the config file that is imported at the beginning
of the script. The GAMS code files must be stored under the path: root_dir/opt/. '''

import pandas as pd
import gamstransfer as gt
from medea_data_atde import compile_symbols
from config import ROOT_DIR
from pathlib import Path
from medea.execute import run_medea

#define possible h2 prices
h2_price_list = list(range(30,100,10))
#define scenario
scenario = 'h_2'
storyline = ['_', '_wind_constraint_', '_windpv_constraint_']


############# define  input parameters that are the same for all scenarios
root_dir = Path(ROOT_DIR)
timeseries = root_dir / 'data' / 'processed' / 'time_series.csv'
zones = ['AT', 'DE']
year = 2016
#initiate h2_price df
h2_price = pd.DataFrame()
h2_price.loc['hydrogen','h_2'] = 90; #place holder that gets replaced in the for loop


#define additional demand from iron making:
# h2 scenario
AT_H2 = 7294.23/8760
AT_H2_el = 2210.74/8760
DE_H2_el = 11985.86/8760
DE_H2 = 39546.69/8760
#electrification scenario
AT_el = 11127.9/8760
DE_el = 60331.5/8760
no_H2 = 0 # adds 0 H2 demand to each hour

#define additional el and h2 demand according to scenario
additional_demand = dict()
if scenario=='el':
    additional_demand['AT'] = pd.DataFrame({'h2': [no_H2], 'el': [AT_el]})
    additional_demand['DE'] = pd.DataFrame({'h2': [no_H2], 'el': [DE_el]})
if scenario=='h_2':
    additional_demand['AT'] = pd.DataFrame({'h2': [AT_H2], 'el': [AT_H2_el]})
    additional_demand['DE'] = pd.DataFrame({'h2': [DE_H2], 'el': [DE_H2_el]})
#create sets and parameters
sets, parameters = compile_symbols(root_dir, timeseries, zones, year, additional_demand,h2_price)

################ for loop to run model for every entry in h2_price_list ###################
for j in storyline:
    for i in h2_price_list:
        run_id = scenario + j + str(i) #name of iteration
        #change PRICE_TRADE from place holder value to i
        parameters['PRICE_TRADE'][1].loc[0,'value'] = i

        ############# write gdx file #################
        md = gt.Container()
        set_clct = {}
        for key, df in sets.items():
            set_clct[key] = gt.Set(md, key, records=df)
        pm_clct = {}
        for key, lst in parameters.items():
            pm_clct[key] = gt.Parameter(md,  key, lst[0], records=lst[1], description=lst[2])
        YEAR = gt.Parameter(md, 'YEAR', [], records=pd.DataFrame([year]), description='year of simulation data')
        export_location = root_dir / 'opt' / f'medea_{run_id}_data.gdx'
        md.write(str(export_location))

        ############### run medea #################
        gams_dir = Path('c:/GAMS/38')
        project_dir = root_dir / 'opt'
        model_gms = project_dir / f'medea_main_final{j}.gms'
        #run_id defines names of input and output gdx
        # --> gdx_in = medea_run_id_data.gdx in project_dir
        # --> gdx_out = medea_out_run_id.gdx
        run_medea(gams_dir, project_dir, model_gms, project=None, run_id=run_id)

