import os
import shutil

from wmt.config import site
from wmt.models.submissions import prepend_to_path
from wmt.utils.hook import find_simulation_input_file


file_list = [#'rti_file',
	     'DEM_file',
             'pixel_file']
choices_map = {
    'Yes': 1,
    'No': 0
}


def lowercase_choice(choice):
    """Formats a string for consumption by TopoFlow.

    Parameters
    ----------
    choice : str
      A parameter choice from WMT.

    """
    import string
    return string.join(choice.split(), '_').lower()


def get_typeof_parameter(parameter_value):
    """Get the TopoFlow type of a parameter."""
    try:
        float(parameter_value)
    except ValueError:
        return 'string'
    else:
        return 'float'


def assign_parameter_type_and_value(env):
    """Assign the value of a TopoFlow input parameter.

    A subset of TopoFlow input parameters can take a scalar value, or,
    through an uploaded file, a time series, a grid, or a grid
    sequence. This function assigns the parameter a scalar value, or
    the name of a file, based on the user's selection in WMT.

    Parameters
    ----------
    env : dict
      A dict of component parameter values from WMT.

    """
    for key in env.copy().iterkeys():
        if key.endswith('_type'):
            key_root = str(key[:-5])
            if env[key] == 'Scalar':
                env[key_root] = env[key_root + '_scalar']
            else:
                env[key_root] = env[key_root + '_file']
                file_list.append(key_root)
            env['typeof_' + key_root] = get_typeof_parameter(env[key_root])


def execute(env):
    """Perform pre-stage tasks for running a component.

    Parameters
    ----------
    env : dict
      A dict of component parameter values from WMT.

    """
    env['n_steps'] = int(round(float(env['run_duration']) / float(env['dt'])))
    env['save_grid_dt'] = float(env['dt'])
    env['save_pixels_dt'] = float(env['dt'])

    # TopoFlow needs site_prefix and case_prefix.
    env['site_prefix'] = os.path.splitext(env['DEM_file'])[0]
    env['case_prefix'] = 'scenario'

    # If no pixel_file is given, let TopoFlow make one.
    if env['pixel_file'] == 'off':
        file_list.remove('pixel_file')
        env['pixel_file'] = '_outlets.txt'

    assign_parameter_type_and_value(env)

    env['VARIABLE_DT_TOGGLE'] = choices_map[env['VARIABLE_DT_TOGGLE']]
    env['INIT_COND_TOGGLE'] = choices_map[env['INIT_COND_TOGGLE']]
    env['GENERIC_ICE_TOGGLE'] = choices_map[env['GENERIC_ICE_TOGGLE']]
    env['ICEFLOW_TOGGLE'] = choices_map[env['ICEFLOW_TOGGLE']]
    env['ICESLIDE_TOGGLE'] = choices_map[env['ICESLIDE_TOGGLE']]
    env['FREEZE_ON_TOGGLE'] = choices_map[env['FREEZE_ON_TOGGLE']]

    # Default files common to all TopoFlow components are stored with the
    # topoflow component metadata.
    prepend_to_path('WMT_INPUT_FILE_PATH',
                    os.path.join(site['db'], 'components', 'topoflow', 'files'))
    for fname in file_list:
        src = find_simulation_input_file(env[fname])
        shutil.copy(src, os.curdir)
