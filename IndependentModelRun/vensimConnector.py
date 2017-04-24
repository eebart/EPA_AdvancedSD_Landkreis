'''
Adapted from EMA Workbench
https://github.com/quaquel/EMAworkbench

by default it is assumed the dll is readily available. If this generates an
exception, you have to find the location of the dll and either copy it to
C:\Windows\System32 and/or C:\Windows\SysWOW64, or use::

    vensim = ctypes.windll.LoadLibrary('location of dll')

Typically, the dll can be found in ../AppData/Local/Vensim/vendll32.dll

Created 2017
@author: eebart
'''
import ctypes
import numpy as np

__all__ = ['be_quiet',
           'load_model',
           'run_simulation',
           'get_varattrib',
           'get_value',
           'set_value',
           'get_data',
           'command']

try:
    WindowsError # @UndefinedVariable
except NameError:
    WindowsError = None

def be_quiet(quietflag=2):
    '''
    this allows you to turn off the work in progress dialog that Vensim
    displays during simulation and other activities, and also prevent the
    appearance of yes or no dialogs.

    use 0 for normal interaction, 1 to prevent the appearance of any work
    in progress windows, and 2 to also prevent the appearance of any
    interrogative dialogs'
    '''
    if quietflag > 2:
        raise Exception("incorrect value for quietflag")

    return vensim.vensim_be_quiet(quietflag)

def load_model(file_name):
    '''
    load the model

    Parameters
    ----------
    file_name : str file name of model, relative to working directory

    Raises
    -------
    Exception if the model cannot be loaded.

    Note: only works for .vpm files
    '''
    try:
        command("SPECIAL>LOADMODEL|"+str(file_name))
    except Exception as w:
        raise Exception("vensim file not found")

def run_simulation(file_name):
    '''
    Convenient function to run a model and store the results of the run in
    the specified .vdf file. The specified output file will be overwritten
    by default

    Parameters
    ----------
    file_name : str
                the file name of the output file relative to the working
                directory

    Raises
    ------
    Exception if running the model failed in some way.
    '''

    file_name = str(file_name)
    try:
        command("SIMULATE>RUNNAME|"+file_name+"|O")
        command("MENU>RUN|o")
    except Exception as e:
        raise Exception("Problem running simulation: {}".format(str(e)))

def get_varattrib(varname, attribute):
    '''
    This function can be used to access the attributes of a variable.

    Parameters
    ----------
    varname : str
              name for which you want attribute
    attribute : int
                attribute you want

    Notes
    -----

    ====== =============
    number meaning
    ====== =============
    1      Units,
    2      the comment,
    3      the equation,
    4      causes,
    5      uses,
    6      initial causes only,
    7      active causes only,
    8      the subscripts the variable has,
    9      all combinations those subscripts create,
    10     the combination of subscripts that would be used by a graph tool,
    11     the minimum value set in the equation editor,
    12     the maximum and
    13     the range,
    14     the variable type (returned as "Level" etc) and
    15     the main group of a variable
    ====== =============

    '''
    buf = ctypes.create_string_buffer(''.encode('utf-8'), 10)
    maxBuf = ctypes.c_int(10)

    bufferlength = vensim.vensim_get_varattrib(varname.encode('utf-8'),
                                               attribute,
                                               buf,
                                               maxBuf)
    if bufferlength == -1:
        raise Exception("variable {} not found when getting attribute {}".format(varname, attribute))

    buf = ctypes.create_string_buffer(''.encode('utf-8'), int(bufferlength))
    maxBuf = ctypes.c_int(int(bufferlength))
    vensim.vensim_get_varattrib(varname.encode('utf-8'), attribute, buf, maxBuf)

    result = repr(buf.raw.decode('utf-8'))
    result = result.strip()
    result = result.rstrip("'")
    result = result.lstrip("'")
    result = result.split(r"\x00")
    result = [varname for varname in result if len(varname) != 0]

    return result

def get_value(name):
    '''
    This function returns the value of a variable during a simulation, as a
    game is progressing, or during simulation setup

    Parameters
    ----------
    name : str
           the name of variable for which one wants to retrieve the value.

    '''
    value = ctypes.c_float(0)
    return_val = vensim.vensim_get_val(name.encode('utf-8'), ctypes.byref(value))
    if return_val == 0:
        raise Exception("variable {} not found when getting value.".format(name))

    return value.value

def set_value(variable, value):
    '''
    set the value of a variable to value

    current implementation only works for lookups and normal values. In case
    of a list, a lookup is assumed, else a normal value is assumed.
    See the DSS reference supplement, p. 58 for details.

    Parameters
    ----------
    variable : str
               name of the variable to set.
    value : int, float, or list
            the value for the variable. **note**: the value can be either a
            list, or an float/integer. If it is a list, it is assumed the
            variable is a lookup.
    '''
    variable = str(variable)

    if isinstance(value, list):
        value = [str(entry) for entry in value]
        command("SIMULATE>SETVAL|"+variable+"("+ str(value)[1:-1] + ")")
    else:
        try:
            command("SIMULATE>SETVAL|"+variable+"="+str(value))
        except:
            warning('variable \'' +variable+'\' not found when setting value')

def get_data(filename, variable_name, tname="Time"):
    '''
    Retrieves data from simulation runs or imported data sets. In contrast
    to the Vensim DLL, this method retrieves all the data, and not only the
    data for the specified length.

    Parameters
    ----------
    filename : str
               the name of the .vdf file that contains the data
    variable_name : str
             the name of the variable to retrieve data on
    tname : str
            the name of the time axis against which to pull the data,
            by default this is Time

    Returns
    -------
    a tuple with an  for an array for varname and and array for tname.

    '''
    vval = (ctypes.c_float * 1)()
    tval = (ctypes.c_float * 1)()
    maxn = ctypes.c_int(0)

    filename = filename.encode('utf-8')
    varname = variable_name.encode('utf-8')
    tname = tname.encode('utf-8')

    return_val = vensim.vensim_get_data(filename,
                                        varname,
                                        tname,
                                        vval,
                                        tval,
                                        maxn)

    if return_val == 0:
        raise Exception("variable "+variable_name+" not found in dataset when retrieving value")

    vval = (ctypes.c_float * int(return_val))()
    tval = (ctypes.c_float * int(return_val))()
    maxn = ctypes.c_int(int(return_val))

    return_val = vensim.vensim_get_data(filename,\
                                         varname,\
                                         tname,\
                                         vval,\
                                         tval,\
                                         maxn)

    vval = np.ctypeslib.as_array(vval)
    tval = np.ctypeslib.as_array(tval)

    return vval, tval

def command(command):
    '''execute a command, for details see chapter 5 of the vensim DSS manual'''

    return_val = vensim.vensim_command(command.encode('utf-8'))
    if return_val == 0:
        raise Exception("command failed "+command)
    return return_val

def add_dll():
    try:
        WindowsError # @UndefinedVariable
    except NameError:
        WindowsError = None

    try:
        vensim_single = ctypes.windll.vendll32
    except AttributeError:
        vensim_single = None
    except WindowsError:
        vensim_single = None

    try:
        vensim_double = ctypes.windll.LoadLibrary('C:\Windows\SysWOW64\VdpDLL32.dll')
    except AttributeError:
        vensim_double = None
    except WindowsError:
        vensim_double = None

    global vensim
    if vensim_single and vensim_double:
        vensim = vensim_single
        print("both single and double precision vensim available, using single")
    elif vensim_single:
        vensim = vensim_single
        print('using single precision vensim')
    elif vensim_double:
        vensim = vensim_double
        print('using single precision vensim')
    else:
        print("vensim dll not found, vensim functionality not available")

add_dll()
