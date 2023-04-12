from enum import Enum
import openai
import re
import ast
import textwrap
from colorama import Fore, Style, init as init_colorama
import dotenv
import os


class GPTClient:
    def __init__(self):
        init_colorama()
        dotenv.load_dotenv()
        model = os.getenv("OPENAI_CHAT_MODEL")

        if model:
            self.model = model
        else:
            self._print_formatted_error("Can not find the model name!")

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
        else:
            self._print_formatted_error("Can not find the OpenAI API key!")

    def generate_problem_statement(self):
        # Call GPT API to generate a problem statement for a coding challenge
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user", "content": "Generate a coding challenge problem statement with description, "
                                               "input format, output format, constraints, and example inputs and "
                                               "outputs."
                },
                {
                    "role": "assistant",
                    "content": "Generate a set of input/output examples with inputs and outputs that can be parsed "
                               "using ast.literal_eval() in Python. The input/output format must adhere to the "
                               "following structure:\n\n1. In: [input_1]\nOut: [output_1]\n2. In: [input_2]\nOut: ["
                               "output_2]\n...\n\nPlease ensure that 'In:' and 'Out:' keywords are only used to "
                               "denote the input and output examples in the response. Additionally, provide examples "
                               "with a variety of Python literals, including tuples, dictionaries, lists, booleans, "
                               "and numerical values. Verify that the generated statement contains the 'In:' and "
                               "'Out:' test cases before returning the result."
                }
            ],
            temperature=1,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        # Extract the generated problem statement from the response
        problem_statement = response.choices[0].message.content.strip()
        self._print_formatted_problem(problem_statement)

        # Parse the problem statement to extract test cases
        test_cases = self.parse_test_cases(problem_statement)
        self._print_formatted_test_cases(test_cases)

        return problem_statement, test_cases

    def update_problem_statement(self, problem_statement, feedback):
        # Call GPT API to generate a problem statement for a coding challenge
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user", "content": f"{problem_statement}\nThe problem statement above does not seem to "
                                               f"contain the correct input / output. This is the possible issue: \n "
                                               f"{feedback}. Please review the test cases and correct and regenerate "
                                               f"the statement."
                },
                {
                    "role": "assistant",
                    "content": "The input/output format must adhere to the "
                               "following structure:\n\n1. In: [input_1]\nOut: [output_1]\n2. In: [input_2]\nOut: ["
                               "output_2]\n...\n\nPlease ensure that 'In:' and 'Out:' keywords are only used to "
                               "denote the input and output examples in the response."
                }
            ],
            temperature=0.4,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        # Extract the generated problem statement from the response
        problem_statement = response.choices[0].message.content.strip()
        self._print_formatted_problem(f"UPDATE:\n{problem_statement}")

        # Parse the problem statement to extract test cases
        test_cases = self.parse_test_cases(problem_statement)
        self._print_formatted_test_cases(test_cases)

        return problem_statement, test_cases

    def parse_test_cases(self, problem_statement):
        # Use regular expressions to extract test case information
        input_pattern = re.compile(r"In:\s*(.+)")
        output_pattern = re.compile(r"Out:\s*(.+)")

        input_matches = input_pattern.findall(problem_statement)
        output_matches = output_pattern.findall(problem_statement)

        # Combine inputs and outputs into test cases
        test_cases = list(zip(input_matches, output_matches))

        # Process inputs and outputs, e.g., convert to tuples, lists, or other data structures
        processed_test_cases = []
        for case_input, expected_output in test_cases:
            # Process input and output based on the problem statement format
            processed_input = ast.literal_eval(case_input)
            processed_output = ast.literal_eval(expected_output)

            processed_test_cases.append((processed_input, processed_output))

        return processed_test_cases

    def generate_algorithm(self, problem_statement):
        # Call GPT API with the problem statement to generate potential solution code
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"{problem_statement}\n\nPlease provide a Python function to solve the above problem. The "
                           "generated code should be complied without any additional modification. So, no comments, "
                           "markdown, code fence, etc in the response."
            }],
            temperature=0.3,
            max_tokens=350,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extract the generated solution code from the response
        solution_code = response.choices[0].message.content.strip()
        self._print_formatted_solution(solution_code)
        return solution_code

    def _print_formatted_problem(self, problem_statement):
        separator = "=" * 80
        print(Fore.CYAN + separator)
        print(Fore.GREEN + "Problem Statement:\n")
        print(Fore.RESET + textwrap.fill(problem_statement, width=80))

    def _print_formatted_test_cases(self, test_cases):
        for index, (input_value, output_value) in enumerate(test_cases):
            print(Fore.LIGHTMAGENTA_EX + f"Test Case {index + 1}: Input: {input_value} Expected: {output_value}")
        print(Fore.RESET)

    def _print_formatted_solution(self, solution_code):
        separator = "=" * 80
        print(Fore.CYAN + separator)
        print(Fore.GREEN + "Solution Code:\n")
        print(Fore.LIGHTGREEN_EX + solution_code)
        print(Fore.CYAN + separator)
        print(Style.RESET_ALL)  # Reset color to default

    def _print_formatted_error(self, error):
        print(Fore.RED + error)
        print(Style.RESET_ALL)
