import unittest
from src.code_compiler import test_code, extract_function_name, execute_code, TestError


class TestCodeCompilerTester(unittest.TestCase):
    def test_extract_function_name(self):
        code = ("def test_function():\n"
                "   pass\n")
        self.assertEqual(extract_function_name(code), "test_function")

    def test_execute_code(self):
        code = 'print("Hello, World!")'
        self.assertEqual(execute_code(code).strip(), "Hello, World!")

    def test_test_code(self):
        code = (
            "def add(a, b):\n"
            "    return a + b")
        test_cases = [((1, 2), 3), ((3, 4), 7), ((5, 6), 11)]
        result, feedback, error = test_code(code, test_cases)
        self.assertTrue(result)
        self.assertIsNone(feedback)
        self.assertIsNone(error)

        code = (
            "def add(a, b):\n"
            "   return a - b")
        result, feedback, error = test_code(code, test_cases)
        self.assertFalse(result)
        self.assertIsNotNone(feedback)
        self.assertEqual(error, TestError.RUNTIME)

        code = (
            "def add(a, b)\n"
            "    return a + b")

        result, feedback, error = test_code(code, [])
        self.assertFalse(result)
        self.assertIsNotNone(feedback)
        self.assertEqual(error, TestError.COMPILATION)

        code = (
            "def add(a, b):\n"
            "   1 / 0\n"
            "   return a + b")

        result, feedback, error = test_code(code, test_cases)
        self.assertFalse(result)
        self.assertIsNotNone(feedback)
        self.assertEqual(error, TestError.RUNTIME)


if __name__ == "__main__":
    unittest.main()
