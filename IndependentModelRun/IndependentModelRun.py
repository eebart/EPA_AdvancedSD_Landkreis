import tarfile
import os
import numpy as np
import pandas as pd

from vensimConnector import *

class Result():
    def __init__(self, outcome_var, outcomes):
        self.variable = outcome_var
        self.outcomes = outcomes

class Case():
    def __init__(self, ident, name='', variables={}):
        self.id = ident
        self.name = name if name != '' else ident
        self.vars = variables
        self.result_file = ''
        self.results = []

class Model():

    def __init__(self, model_name, wd, model_file, cases=[]):
        if not model_file.endswith('.vpm'):
            raise ValueError('model file should be a vpm file')

        path_to_file = os.path.join(wd, model_file)
        if not os.path.isfile(path_to_file):
            raise ValueError('cannot find model file')

        self.name = model_name
        self.working_directory = wd
        self.model_file = model_file

        self.results_dir = 'results/'
        try:
            os.stat(self.results_dir)
        except:
            os.mkdir(self.results_dir)

        self.outcomes = ['TIME']
        self.cases = cases

    def build_cases_from_dict(self,case_dict):
        curr_index = 0
        name, ident = '', ''

        self.cases = []
        for record in case_dict:
            if 'id' in record:
                ident = record['id']
                del record['id']
            else:
                ident = str(curr_index)

            if 'name' in record:
                name = record['name']
                del record['name']

            self.cases.append(Case(ident,name,record))
            curr_index += 1

    def add_outcome(self, outcome):
        self.outcomes.append(outcome)

    def add_outcomes(self, outcome_list):
        self.outcomes.extend(outcome_list)

    def __model_init(self):
        fn = os.path.join(self.working_directory, self.model_file)
        load_model(fn) #EMA
        be_quiet() #EMA

        try:
            initialTime  = get_value('INITIAL TIME')
            finalTime = get_value('FINAL TIME')
            timeStep = get_value('TIME STEP')
            savePer = get_value('SAVEPER')

            if savePer > 0:
                timeStep = savePer

            self.run_length = int((finalTime - initialTime)/timeStep +1)

        except Exception:
            raise Exception

    def __parse_lookup(self, lookup_file, case):
        df = pd.read_csv(lookup_file,encoding='UTF-8')

        vals = {}
        if 'id' in df.columns:
            ids = df.loc[df['id'] == case.id]
            if ids.shape[0] > 0:
                vals = ids.iloc[0].to_dict()
        if 'name' in df.columns:
            names = df.loc[df['name'] == case.name]
            if names.shape[0] == 1:
                vals = names.iloc[0].to_dict()


        to_set = []
        for key, val in vals.items():
            if key != 'name' and key != 'id':
                to_set.append((float(key),val))

        return to_set

    def __reset_model(self):
        self._output = {}

    def run_cases(self):
        self.__model_init()

        results_files = {}

        for index, case in enumerate(self.cases):

            for key, value in case.vars.items():
                var_type = get_varattrib(key, 14) #get the type of the variable
                if var_type[0].lower() == 'lookup':
                    #it's a lookup, value is actually filename for lookup
                    lookup_value = self.__parse_lookup(value, case)
                    set_value(key, lookup_value)
                else:
                    set_value(key, value)

            try:
                print("Running simulation for '{}'".format(case.name))
                case.result_file = self.results_dir + case.id + '_' + case.name + '.vdf'
                run_simulation(case.result_file)
            except Exception:
                raise

        self.get_results()

    def __check_data(self, result):
        error = False
        if len(result[0]) != self.run_length:
            data = np.empty((self.run_length))
            data[:] = np.NAN
            data[0:len(result[0])] = result
            result = data
            error = True
        return result, error

    def get_results(self):
        error = False
        badcount = 0

        for case in self.cases:
            result_filename = os.path.join(self.working_directory, case.result_file)
            for variable in self.outcomes:
                res = get_data(result_filename, variable)
                result, er = self.__check_data(np.asarray(res))
                error = error or er
                case.results.append(Result(variable, np.array(result)))

            if error:
                badcount += 1

        print('{} out of {} cases ran into difficulties.'.format(badcount, len(self.cases)))

def save_results(cases, results_file):
    keys = set()

    results_frames = {}
    time_frame = []
    for case in cases:
        for result in case.results:
            if (result.variable == 'TIME'):
                timeoutcome = result.outcomes[0]
                timeoutcome = timeoutcome[np.logical_not(np.isnan(timeoutcome))].tolist()
                if len(time_frame) < len(timeoutcome):
                    time_frame = timeoutcome
            else:
                outcome_arr = [case.id,case.name]
                outcome_arr.extend(result.outcomes[0])
                if result.variable not in results_frames:
                    results_frames[result.variable] = [outcome_arr]
                else:
                    results_frames[result.variable].append(outcome_arr)

    tar = tarfile.open(results_file, 'w:gz')

    columns = ['id','name']
    columns.extend(time_frame)
    for key in results_frames:
        df = pd.DataFrame(results_frames[key],columns=columns)
        filename = 'outcome_'+key+'.csv'
        df.to_csv(filename, index=False)
        tar.add(filename)
        os.remove(filename)

    tar.close()
