# Stack Frame Extractor

`stack_frame_extractor` captures the current call stack and returns a list of
`(function_name, file_path, line_number)` tuples suitable for attaching to
error contexts or log records.

## Usage

```python
from stack_frame_extractor import extract_stack_frames

def risky_function():
    frames = extract_stack_frames()
    for function_name, file_path, line_number in frames:
        print(f"{function_name} at {file_path}:{line_number}")

risky_function()
```

This prints the call stack starting with the caller of `extract_stack_frames`
and continuing outward.

## Why this exists

When building error handling and observability tooling, it is common to need a
lightweight snapshot of the call stack that can be serialized and attached to
exception metadata.  The standard library offers `inspect.stack()` and
`traceback.extract_stack()`, but neither returns the exact shape we need
directly.  This library wraps `inspect.stack()` and normalizes the output into
simple tuples.

The trade-off is that we use `inspect.stack()`, which creates frame objects and
must be used carefully to avoid reference cycles.  The implementation deletes
frame references as soon as possible to limit this impact.

## Edge case

If a frame has no associated code object (for example, a frame created by the C
stack), the function name and file path are reported as `"<unknown>"`.  The
line number is taken from `frame_info.lineno`, which may be 0 in rare cases.
Callers should not assume line numbers are always positive when processing
unknown frames.
