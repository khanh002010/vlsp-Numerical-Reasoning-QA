"""
Symbolic Executor for the ViNumQA Pipeline.
Takes a reasoning program, executes it via Python, and returns the final result.
"""

from vinumqa.utils.dsl_parser import parse_program, execute_program, validate_program

class SymbolicExecutor:
    def __init__(self):
        print("Initializing Symbolic Executor...")

    def execute(self, program_str: str, tables=None, charts=None) -> str:
        """
        Validates and executes the program.
        Returns the result as a string or an error message.
        """
        # Validate
        is_valid, msg = validate_program(program_str)
        if not is_valid:
            return f"Error: {msg}"
            
        try:
            steps = parse_program(program_str)
            
            # The execution relies on the table and chart context.
            # In our current DSL parser, we return 'None' for chart/table lookups 
            # if the actual data dict isn't provided. 
            # In a full pipeline, the 'Chart-to-Table' module would feed actual tables 
            # and this executor would resolve chart/table lookups using the data.
            # 
            # Since the competition tests reasoning (and LLMs provide arguments directly),
            # the step arguments extracted by the LLM are usually numeric or strings. 
            # If the LLM successfully replaces chart_at / table_max with their values,
            # we just execute math. 
            # But ViNumQA DSL requires the program to look up explicitly:
            # e.g., table_max(Table 1; Đầu tư công; 2021; 2025F)
            
            results = execute_program(steps, tables=tables, charts=charts)
            
            # The final result is the output of the last step
            if len(steps) > 0:
                final_step_id = steps[-1].step_id
                final_result = results.get(final_step_id)
                return str(final_result)
            else:
                return "Error: Empty program"
                
        except Exception as e:
            return f"Execution Error: {str(e)}"

if __name__ == "__main__":
    executor = SymbolicExecutor()
    print("Symbolic Executor is ready.")
