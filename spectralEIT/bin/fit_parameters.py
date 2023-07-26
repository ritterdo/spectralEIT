import yaml
import re

from importlib import import_module

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

## working direction is ./spectralEIT/
fit_params_bound = yaml.safe_load(open("data/config/fitParams.yaml"))
for key in fit_params_bound.keys():
    for i, value in enumerate(fit_params_bound[key]):
        if type(value) == str:
            minus = False
            if value.startswith("-"):
                minus = True
                value = value[1:]
            module_, func = value.rsplit(".", maxsplit=1)
            m = import_module(module_)
            if minus:
                fit_params_bound[key][i] = -getattr(m, func)
            else:
                fit_params_bound[key][i] = getattr(m, func)
fit_params_list = fit_params_bound.keys()
