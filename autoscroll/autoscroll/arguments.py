from argparse import SUPPRESS, HelpFormatter, ArgumentParser, _ArgumentGroup
from typing import Any, Dict


def parse_arguments(**arguments: Any) -> Dict[str, Any]:
    result = {}
    for key, value in arguments.items():
        key_split = key.split('-')
        group = key_split[0]
        name = ''.join(key_split[1:]).replace('-', '_')
        if group not in result:
            result[group] = {}
        result[group][name] = value
    return result


class ArgparseFormatter(HelpFormatter):

    # do not split lines that start with 'R|'
    # https://stackoverflow.com/questions/3853722/how-to-insert-newlines-on-argparse-help-text
    def _split_lines(self, text: str, width: int):
        if not text.startswith('R|'):
            return super()._split_lines(text, width)
        result = []
        for line in text[2:].splitlines(keepends=True):
            result.extend(super()._split_lines(line, width))
        return result

    # do not format the description
    # built-in argparse class argparse.RawDescriptionHelpFormatter
    def _fill_text(self, text: str, width: int, indent: str):
        return '\n'.join(indent + line
                         for line in text.splitlines(keepends=True))

    # change how 'metavar' is displayed
    # https://stackoverflow.com/questions/23936145/python-argparse-help-message-disable-metavar-for-short-options
    def _format_action_invocation(self, action):
        if not action.option_strings:
            return self._metavar_formatter(action, action.dest)(1)[0]
        parts = action.option_strings.copy()
        # option takes no arguments -> -s, --long
        # option takes arguments:
        #    default output -> -s ARGS, --long ARGS
        #    changed output -> -s, --long type
        if action.nargs != 0:
            parts[-1] += f' {action.type.__name__}'
        return ', '.join(parts)

    # add default value to the end
    # built-in argparse class argparse.ArgumentDefaultsHelpFormatter
    def _get_help_string(self, action):
        if action.nargs == 0 or action.default is SUPPRESS or not action.default:
            return action.help
        return f'{action.help}\n[default: %(default)s]'


class _ArgparseArgumentGroup(_ArgumentGroup):

    def add_arguments(self, **arguments: Dict[str, Dict[str, Any]]
                      ) -> '_ArgparseArgumentGroup':
        for name, kwargs in arguments.items():
            flags = f'-{self.title[0]}{name[0]}', f'--{self.title}-{name}'
            self.add_argument(*flags, **kwargs)
        return self


class ArgparseParser(ArgumentParser):

    # overloading
    def add_argument_group(self, *args,
                           parameters: Dict[str, Dict[str, Any]] = None,
                           **kwargs):
        group = _ArgparseArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        if parameters is not None:
            group.add_arguments(**parameters)
        return group

    # add a bunch of arguments and argument groups in one go
    def add_arguments(self, **groups: Dict[str, Any]) -> 'ArgparseParser':
        for name, parameters in groups.items():
            self.add_argument_group(title=name, **parameters)
        return self