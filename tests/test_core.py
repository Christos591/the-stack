"""Tests for stack_frame_extractor.core."""

import os
import unittest
from typing import List, Tuple

from stack_frame_extractor import extract_stack_frames


class TestExtractStackFrames(unittest.TestCase):
    def test_returns_list_of_tuples(self) -> None:
        frames = extract_stack_frames()
        self.assertIsInstance(frames, list)
        for frame in frames:
            self.assertIsInstance(frame, tuple)
            self.assertEqual(len(frame), 3)
            function_name, file_path, line_number = frame
            self.assertIsInstance(function_name, str)
            self.assertIsInstance(file_path, str)
            self.assertIsInstance(line_number, int)

    def test_excludes_itself_from_stack(self) -> None:
        frames = extract_stack_frames()
        self.assertTrue(len(frames) > 0)
        self.assertNotEqual(frames[0][0], "extract_stack_frames")

    def test_outermost_frame_is_test_runner(self) -> None:
        frames = extract_stack_frames()
        # The outermost frame in unittest execution is typically the main
        # module or the test runner.  We do not assert a specific name, only
        # that it is present and not empty.
        self.assertIsNotNone(frames[-1][0])
        self.assertNotEqual(frames[-1][0], "")

    def test_caller_function_name_is_correct(self) -> None:
        def inner_call() -> List[Tuple[str, str, int]]:
            return extract_stack_frames()

        frames = inner_call()
        self.assertEqual(frames[0][0], "inner_call")

    def test_line_number_points_to_call_site(self) -> None:
        def inner_call() -> List[Tuple[str, str, int]]:
            return extract_stack_frames()

        # The call to extract_stack_frames is on the next line.
        call_line = inner_call.__code__.co_firstlineno + 1
        frames = inner_call()
        self.assertEqual(frames[0][2], call_line)

    def test_file_path_is_current_test_file(self) -> None:
        frames = extract_stack_frames()
        expected_path = os.path.abspath(__file__)
        self.assertEqual(frames[0][1], expected_path)

    def test_nested_calls_preserve_order(self) -> None:
        def first() -> List[Tuple[str, str, int]]:
            return second()

        def second() -> List[Tuple[str, str, int]]:
            return extract_stack_frames()

        frames = first()
        # The stack from innermost to outermost after extract_stack_frames is:
        # second, first, test method.
        self.assertEqual(frames[0][0], "second")
        self.assertEqual(frames[1][0], "first")
        self.assertIn("test_nested_calls_preserve_order", frames[2][0])

    def test_all_function_names_are_non_empty(self) -> None:
        frames = extract_stack_frames()
        for function_name, _, _ in frames:
            self.assertIsInstance(function_name, str)
            self.assertNotEqual(function_name, "")

    def test_all_file_paths_are_absolute_or_unknown(self) -> None:
        frames = extract_stack_frames()
        for _, file_path, _ in frames:
            if file_path != "<unknown>":
                self.assertTrue(os.path.isabs(file_path) or file_path.startswith("<"))

    def test_all_line_numbers_are_positive(self) -> None:
        frames = extract_stack_frames()
        for _, _, line_number in frames:
            self.assertGreater(line_number, 0)


if __name__ == "__main__":
    unittest.main()
