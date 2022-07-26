"""Use `relative path` in traceback stack.

(Python 3.9.2)
"""

import sys
import traceback
from pathlib import Path


def _relative_print_exception(etype, value, tb, limit=None, file=None, chain=True):
    if file is None:
        file = sys.stderr
    for line in _RelativeTracebackException(type(value), value, tb, limit=limit).format(
        chain=chain
    ):
        print(line, file=file, end="")


class _RelativeStackSummary(traceback.StackSummary):
    """
    replace:
        - `StackSummary`
    """

    @classmethod
    def from_list(klass, a_list):
        result = _RelativeStackSummary()
        for frame in a_list:
            if isinstance(frame, traceback.FrameSummary):
                result.append(frame)
            else:
                filename, lineno, name, line = frame
                result.append(traceback.FrameSummary(filename, lineno, name, line=line))
        return result

    def format(self):
        result = []
        last_file = None
        last_line = None
        last_name = None
        count = 0
        for frame in self:
            if (
                last_file is None
                or last_file != frame.filename
                or last_line is None
                or last_line != frame.lineno
                or last_name is None
                or last_name != frame.name
            ):
                if count > traceback._RECURSIVE_CUTOFF:
                    count -= traceback._RECURSIVE_CUTOFF
                    result.append(
                        f'  [Previous line repeated {count} more '
                        f'time{"s" if count > 1 else ""}]\n'
                    )
                last_file = frame.filename
                last_line = frame.lineno
                last_name = frame.name
                count = 0
            count += 1
            if count > traceback._RECURSIVE_CUTOFF:
                continue
            row = []
            # overrided
            filename = Path(frame.filename)
            if filename.is_relative_to(Path.cwd()):
                filename = f'./{Path(frame.filename).relative_to(Path.cwd())}'
            row.append(
                '  File "{}", line {}, in {}\n'.format(
                    filename,
                    frame.lineno,
                    frame.name,
                )
            )
            if frame.line:
                row.append('    {}\n'.format(frame.line.strip()))
            if frame.locals:
                for name, value in sorted(frame.locals.items()):
                    row.append('    {name} = {value}\n'.format(name=name, value=value))
            result.append(''.join(row))
        if count > traceback._RECURSIVE_CUTOFF:
            count -= traceback._RECURSIVE_CUTOFF
            result.append(
                f'  [Previous line repeated {count} more '
                f'time{"s" if count > 1 else ""}]\n'
            )
        return result


class _RelativeTracebackException(traceback.TracebackException):
    """
    replace:
        - `StackSummary`
        - `TracebackException`
    """

    def __init__(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        *,
        limit=None,
        lookup_lines=True,
        capture_locals=False,
        _seen=None,
    ):
        if _seen is None:
            _seen = set()
        _seen.add(id(exc_value))
        if (
            exc_value
            and exc_value.__cause__ is not None
            and id(exc_value.__cause__) not in _seen
        ):
            cause = _RelativeTracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen,
            )
        else:
            cause = None
        if (
            exc_value
            and exc_value.__context__ is not None
            and id(exc_value.__context__) not in _seen
        ):
            context = _RelativeTracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen,
            )
        else:
            context = None
        self.__cause__ = cause
        self.__context__ = context
        self.__suppress_context__ = (
            exc_value.__suppress_context__ if exc_value else False
        )
        self.stack = _RelativeStackSummary.extract(
            traceback.walk_tb(exc_traceback),
            limit=limit,
            lookup_lines=lookup_lines,
            capture_locals=capture_locals,
        )
        self.exc_type = exc_type
        self._str = traceback._some_str(exc_value)
        if exc_type and issubclass(exc_type, SyntaxError):
            self.filename = exc_value.filename
            lno = exc_value.lineno
            self.lineno = str(lno) if lno is not None else None
            self.text = exc_value.text
            self.offset = exc_value.offset
            self.msg = exc_value.msg
        if lookup_lines:
            self._load_lines()


def relative_print_exc(limit=None, file=None, chain=True):
    _relative_print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)


def use_relative_except():
    sys.excepthook = _relative_print_exception
