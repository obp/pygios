import gflags
import gflags_multibool
import sys
import os.path
import os
import traceback
from StringIO import StringIO

FLAGS = gflags.FLAGS

gflags_multibool.DEFINE_multibool('verbose', 0, 'Verbosity leve', short_name='v')

gflags.DEFINE_string('name', sys.argv[0], 'Set the name of this daemon as presented to nagios.  This parameter is optional and can be used to overwrite the name parameter provided to pygios_main')

def default_warning(v, help=None):
    if isinstance(v, (str, unicode)):
        gflags.DEFINE_string('warning', v, help or 'Warning threshold', short_name='w')
    elif isinstance(v, int):
        gflags.DEFINE_integer('warning', v, help or 'Warning threshold', short_name='w')
    elif isinstance(v, float):
        gflags.DEFINE_float('warning', v, help or 'Warning threshold', short_name='w')
    else:
        TypeErrpr('default_warning(v); v must be str, int or float, not %s' % type(v))

def default_critical(v, help=None):
    if isinstance(v, (str, unicode)):
        gflags.DEFINE_string('critical', v, help or 'Critical threshold', short_name='c')
    elif isinstance(v, int):
        gflags.DEFINE_integer('critical', v, help or 'Critical threshold', short_name='c')
    elif isinstance(v, float):
        gflags.DEFINE_float('critical', v, help or 'Critical threshold', short_name='c')
    else:
        TypeErrpr('default_critical(v); v must be str, int or float, not %s' % type(v))

def warning_threshold():
    return FLAGS.warning

def critical_threshold():
    return FLAGS.critical


_code = 0
_performance = []
_output = []
_verbosity = 0

def reset():
    global _code, _performance, _output, _verbosity
    _code = 0
    _performance = []
    _output = []
    _verbosity = 0


def warning():
    global _code
    _code = max(_code, 1)


def critical():
    global _code
    _code = max(_code, 2)


class NagiosError(Exception):
    pass


def error(*args):
    raise NagioError(*args)


class P(str): pass


def code_name():
    global _code
    return {0:'OK', 1:'WARNING', 2:'CRITICAL'}.get(_code, 'UNKNOWN')


def more():
    global _verbosity
    _verbosity += 1


def PygiosMain(args=sys.argv, work=None, name=None, stdout=sys.stdout, stderr=sys.stderr, exit=exit):
    _args = args
    global _code
    try:
        args = FLAGS(args)[1:]
    except (gflags.FlagsError, KeyError, IndexError), e:
        stderr.write("%s\nUsage: %s \n%s\n" % (
                e, os.path.basename(_args[0]), FLAGS))
        return exit(3)
    name = FLAGS.name or name or (args and args[0]) or sys.argv[0]

    try:
        for line in work() or []:
            if line is None: continue
            if _verbosity > FLAGS.verbose:
                break
            if isinstance(line, P):
                _performance.append(line)
            elif isinstance(line, (str, unicode)):
                _output.append(line)
            else:
                raise TypeError('Can only yield str/unicode for messages or P for performance messages')
        if not _output:
            _output.append('')
        if _performance:
            stdout.write("%s %s - %s | %s\n" % (
                name,
                code_name(),
                _output[0],
                _performance[0],
                ))
        else:
            stdout.write("%s %s - %s\n" % (
                name,
                code_name(),
                _output[0]
                ))

        stdout.write('\n'.join(_output[1:]))
        if _performance[1:]:
            stdout.write('|')
            stdout.write('\n'.join(_performance[1:]))
        stdout.flush()
        return exit(_code)
    except Exception as e:
        exception_printout = StringIO()
        if FLAGS.verbose:
            traceback.print_exc(file=exception_printout)
        stdout.write("%s UNKNOWN - %s" % (name, exception_printout.getvalue().replace('|', '\\|')))
        stdout.flush()
        return exit(3)

def check(v, msg):
    if v > FLAGS.critical:
        critical()
    elif v > FLAGS.warning:
        warning()
    if msg is not None:
        return msg % (v,)





__ALL__ = 'PygiosMain warning critical NagiosError error perf output more P check'.split()
