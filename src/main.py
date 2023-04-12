from chat_gpt_client import GPTClient
from code_compiler import test_code, TestError
from enum import Enum


class AppState(Enum):
    GENERATE_PROBLEM_STATEMENT = 1
    UPDATE_PROBLEM_STATEMENT = 2
    GENERATE_ALGORITHM = 3
    EXECUTE_SOLUTION = 4
    COMPLETED = 5


def main():
    max_iterations = 10  # Set a maximum number of iterations
    iteration_count = 0
    max_runtime_failures = 2  # Number of retries on runtime error before asking to update the statement
    code_exec_count = 0
    solution_found = False
    problem_statement = None
    feedback = None
    test_cases = None
    solution_code = None
    gpt_client = GPTClient()
    app_state = AppState.GENERATE_PROBLEM_STATEMENT

    while iteration_count < max_iterations and not solution_found:
        iteration_count += 1
        print(f"> Attempt # {iteration_count}:")
        if app_state == AppState.GENERATE_PROBLEM_STATEMENT:
            try:
                print(f"> Generating the problem statement...")
                problem_statement, test_cases = gpt_client.generate_problem_statement()
                app_state = AppState.GENERATE_ALGORITHM
            except Exception as e:
                print(f"> Failed to generate the problem statement: {e}. Retrying...")
        if app_state == AppState.UPDATE_PROBLEM_STATEMENT:
            try:
                print(f"> Updating the problem statement...")
                problem_statement, test_cases = gpt_client.update_problem_statement(problem_statement, feedback)
                app_state = AppState.GENERATE_ALGORITHM
            except Exception as e:
                print(f"> Failed to update the statement: {e}. Retrying...")
        if app_state == AppState.GENERATE_ALGORITHM:
            try:
                print("> Generating the solution algorithm...")
                solution_code = gpt_client.generate_algorithm(problem_statement)
                app_state = AppState.EXECUTE_SOLUTION
            except Exception as e:
                print(f"> Failed to generate the algorithm: {e}. Retrying...")
        if app_state == AppState.EXECUTE_SOLUTION:
            try:
                print("> Executing the solution...")
                test_result, feedback, error = test_code(solution_code, test_cases)
                print("\n> Test result:", "Passed ✅" if test_result else "Failed ❌")
                print("" if feedback is None else f"> Feedback: {feedback}")
                solution_found = test_result
                if solution_found:
                    app_state = AppState.COMPLETED
                elif error:
                    if error is TestError.COMPILATION:
                        app_state = AppState.UPDATE_PROBLEM_STATEMENT
                    elif error is TestError.RUNTIME:
                        code_exec_count += 1
                        if code_exec_count >= max_runtime_failures:
                            app_state = AppState.UPDATE_PROBLEM_STATEMENT
                            code_exec_count = 0
                        else:
                            app_state = AppState.GENERATE_ALGORITHM
            except Exception as e:
                print(f"Failed to execute and test the code: {e}. Retrying...")

    if iteration_count == max_iterations:
        if app_state == AppState.COMPLETED:
            if solution_found:
                print(f"> Process successfully completed after {iteration_count} attempt(s)!")
            else:
                print(f"> Unable to complete the task after {max_iterations} attempt(s)!")


if __name__ == "__main__":
    main()
