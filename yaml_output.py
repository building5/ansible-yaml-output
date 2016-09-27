# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import yaml
import json
import re
import string
import sys
from ansible.plugins.callback import CallbackBase, strip_internal_keys
from ansible.plugins.callback.default import CallbackModule as Default

__metaclass__ = type

# from http://stackoverflow.com/a/15423007/115478
def should_use_block(value):
    """Returns true if string should be in block format"""
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def my_represent_scalar(self, tag, value, style=None):
    """Uses block style for multi-line strings"""
    if style is None:
        if should_use_block(value):
            style = '|'
            # we care more about readable than accuracy, so...
            # ...no trailing space
            value = value.rstrip()
            # ...and non-printable characters
            value = filter(lambda x: x in string.printable, value)
            # ...tabs prevent blocks from expanding
            value = value.expandtabs()
            # ...and odd bits of whitespace
            value = re.sub(r'\x0b|\x0c|\r', '', value)
            # ...as does trailing space
            value = re.sub(r' +\n', '\n', value)
        else:
            style = self.default_style
    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node

yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar

class CallbackModule(Default):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'yaml_log'

    def _dump_results(self, result, indent=None, sort_keys=True, keep_invocation=False):
        if result.get('_ansible_no_log', False):
            return json.dumps(dict(censored="the output has been hidden due to the fact that 'no_log: true' was specified for this result"))

        # All result keys stating with _ansible_ are internal, so remove them from the result before we output anything.
        abridged_result = strip_internal_keys(result)

        # remove invocation unless specifically wanting it
        if not keep_invocation and self._display.verbosity < 3 and 'invocation' in result:
            del abridged_result['invocation']

        # remove diff information from screen output
        if self._display.verbosity < 3 and 'diff' in result:
            del abridged_result['diff']

        dumped = ''

        if 'changed' in abridged_result:
            dumped += 'changed=' + str(abridged_result['changed']).lower() + ' '
            del abridged_result['changed']

        if 'skipped' in abridged_result:
            dumped += 'skipped=' + str(abridged_result['skipped']).lower() + ' '
            del abridged_result['skipped']

        # if we already have stdout, we don't need stdout_lines
        if 'stdout' in abridged_result and 'stdout_lines' in abridged_result:
            del abridged_result['stdout_lines']

        if 'stdout' in abridged_result:
            print(json.dumps(abridged_result['stdout']), file=sys.stderr)

        if abridged_result:
            dumped += '\n'
            dumped += yaml.safe_dump(json.loads(json.dumps(abridged_result, ensure_ascii=False)), width=1000, default_flow_style=False)

        # indent by a couple of spaces
        dumped = '\n  '.join(dumped.split('\n')).rstrip()
        return dumped
