import sys
from io import StringIO
from contextlib import redirect_stdout
from typing import List, Tuple, Optional
import ast
from enum import Enum


class TestError(Enum):
    COMPILATION = 1
    RUNTIME = 2


def execute_code(code):
    # Redirect stdout to capture the output of the code
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        with redirect_stdout(sys.stdout):
            exec(code)
        output = sys.stdout.getvalue()
    except Exception as e:
        output = str(e)
    finally:
        sys.stdout = original_stdout

    return output


def test_code(code: str,
              test_cases: List[Tuple[str, str]]) -> Tuple[bool, Optional[str], Optional[TestError]]:
    # Execute the code and capture any compilation errors
    try:
        exec(code, globals())
    except Exception as e:
        return False, str(e), TestError.COMPILATION

    # Extract the function name from the provided code
    function_name = extract_function_name(code)
    if function_name is None:
        return False, "Function not found!", TestError.COMPILATION

    # Test the code with the provided test cases
    for i, (input_obj, expected_output_obj) in enumerate(test_cases):
        # Call the function and capture any runtime errors
        try:
            output_obj = globals()[function_name](*input_obj) if isinstance(input_obj, tuple) else globals()[
                function_name](input_obj)
            print(f">> Input: {input_obj}\nReturned: {output_obj}")
        except Exception as e:
            return False, str(e), TestError.RUNTIME

        # Compare the output with the expected output
        if output_obj != expected_output_obj:
            error_msg = f"Test case {i + 1} failed: Expected {expected_output_obj}, but got {output_obj}"
            return False, error_msg, TestError.RUNTIME

    # If all test cases pass
    return True, None, None


def extract_function_name(code: str) -> Optional[str]:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None
