from importlib.resources import path as importlib_path


def get_resource_path(resource: str = None) -> str:
    if resource is None:
        file = ''
        addition = ''
    else:
        split = resource.split('/')
        addition = '.'.join(split[0:-1])
        addition = f'.{addition}' if addition else ''
        file = split[-1]
        file = file if file != addition else ''
    return importlib_path(f'linux-autoscroll{addition}', file)
