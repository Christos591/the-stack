"""Core stack frame extraction logic.

The primary goal is to provide a simple, dependency-free way to capture the
current call stack and produce lightweight, JSON-serializable records suitable
for attaching to error contexts or log messages.

Design notes:
- ``inspect.stack()`` is used rather than ``traceback.extract_stack()`` because
  it provides frame objects which let us reliably derive both module file paths
  and function names.  ``traceback.extract_stack()`` would give line numbers but
  not the frame object's code name in every Python implementation.
- We skip the first frame returned by ``inspect.stack()`` because that frame is
  always the call to ``extract_stack_frames`` itself.  Including it would make
  every record start with this utility function, which is noise for error
  context.
"""

from __future__ import annotations

import inspect
from typing import List, Tuple

FrameRecord = Tuple[str, str, int]


def extract_stack_frames() -> List[FrameRecord]:
    """Capture the current call stack.

    Returns:
        A list of ``(function_name, file_path, line_number)`` tuples.
        The first element is the caller of this function, and the last is the
        outermost stack frame.

    The returned file paths are absolute paths to the source files as resolved
    by the running Python interpreter.  If a frame has no associated code
    object (for example, a frame created by the C stack), the function name is
    reported as ``"<unknown>"`` and the file path is ``"<unknown>"``.
    """
    frames: List[FrameRecord] = []

    # inspect.stack() returns frames starting with the current function.
    # We drop the first element (index 0) to exclude this helper itself.
    raw_frames = inspect.stack()[1:]

    for frame_info in raw_frames:
        frame = frame_info.frame
        code = frame.f_code

        function_name = getattr(code, "co_name", "<unknown>")
        file_path = getattr(code, "co_filename", "<unknown>")
        line_number = frame_info.lineno

        frames.append((function_name, file_path, line_number))

    # Explicitly delete frame references to avoid reference cycles that can
    # delay garbage collection of the captured frames.
    del raw_frames

    return frames
