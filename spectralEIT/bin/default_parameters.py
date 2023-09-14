import numpy as np

import os
import yaml
import re

default_params = [
            "width0", "focalLength", "posLC", "prop", "cellLength", "zsteps", "lightShape", "propType", "dt", "rabiFrequency",
            "lcLength", "lossdB", "EITDetune", "f0det", "T", "gammad", "profile", "gaussSteps", "transition", 
            "type", "gamma_coll", "freqStart", "freqStop", "freqSteps"
        ]

loader = yaml.SafeLoader
loader.add_implicit_resolver(
    u'tag:yaml.org,2002:float',
    re.compile(u'''^(?:
     [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
    |[-+]?\\.(?:inf|Inf|INF)
    |\\.(?:nan|NaN|NAN))$''', re.X),
    list(u'-+0123456789.'))

DEFAULT_PARAMETER_DICT = yaml.safe_load( open("data/config/parameters.yaml", 'r'))

for par in default_params:
     if par not in DEFAULT_PARAMETER_DICT.keys():
         raise ValueError("Something wrong with the default parameters: {} not found".format(par))
