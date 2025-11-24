# part 1 imports required libraries and set up 
from openai import OpenAI
from dotenv import load_dotenv
import os
import subprocess
import json
import yaml
import re

load_dotenv()

# part 2 define the execution tool function
def execute_tool(name,args:dict):
    if name =="bash_command":
        try:
            result = subprocess.run(
                args["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                executable="/bin/bash"
            )
            if result.returncode ==0:
                # means the command executed successfully
                return f"Success:\n{result.stdout}" if result.stdout else "Success (no output)"
            else:
                return f"Error {result.returncode}:\n{result.stderr}" if result.stderr else "Unknown error"
        except Exception as e:
            return f"Exception: {str(e)}"
    elif name == "think":
        return f"Thinking recorded: {args['thought']}"
    else:
        return f"Unknown tool: {name}"

# part 3 design the agent with init to load the yaml 
class Agent:
    def __init__(self, agent_name="specification_agent", model_name=None, yaml_path="agent/agent.yaml"):
        with open(yaml_path) as f:
            CONFIG = yaml.safe_load(f)
        if not CONFIG:
            raise ValueError("Invalid YAML file")
        
        self.agent_config = CONFIG['agent'].get(agent_name)
        if not self.agent_config:
            # Fallback for backward compatibility or default
            self.agent_config = CONFIG['agent'].get("specification_agent")

        self.model_name = model_name or self.agent_config.get("model")
        self.tool_schemas = [CONFIG['tools'][t] for t in self.agent_config.get("tools", [])]
        self.system_prompt = self.agent_config.get("system_prompt")
      
        key = os.getenv("DEEPSEEK_API_KEY") if "deepseek" in self.model_name else os.getenv("OPENROUTER_API_KEY")
        base_url = "https://api.deepseek.com" if "deepseek" in self.model_name else "https://openrouter.ai/api/v1"
        self.client = OpenAI(
            api_key=key,
            base_url=base_url
        )
    
    def run(self, user_input, max_turns=10):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        final_response = ""

        for turn in range(max_turns):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tool_schemas if self.tool_schemas else None,
                temperature=self.agent_config.get("temperature", 0.1)
            )
            msg = response.choices[0].message
            print(f"Turn {turn}: raw output: {msg.content[:100]}..." if msg.content else f"Turn {turn}: Tool call")
            
            messages.append(msg)
            
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    try:
                        fn_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        result = execute_tool(fn_name, args)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })
                    except Exception as e:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error executing/parsing tool: {str(e)}"
                        })
            elif msg.content:
                final_response = msg.content
                if response.choices[0].finish_reason == "stop":
                    break
            else:
                break
                
        return final_response

# part 4 design the workflow functions

PROMPT_15 = '''
def task_func(commands_file_path, output_dir_path):
    """
    Execute a list of shell commands read from a CSV file and save the outputs in separate files.
    Each command's output is written to a unique file in the specified output directory.
    If a command fails, the error message along with the exit code is appended to the respective output file.

    Parameters:
    - commands_file_path (str): Path to the CSV file containing shell commands in the first column.
                                The file should not have headers.
    - output_dir_path (str): Path where the outputs of the commands will be saved. If the directory does not exist,
                             it will be created.

    Requirements:
    - subprocess
    - csv
    - os

    Raises:
    - FileNotFoundError: If the commands_file_path does not exist.

    Returns:
    - list of str: A list of paths to the output files created in the output directory, each named as
                   'command_X_output.txt', where X is the command index. If a command execution fails,
                   the output file will contain a descriptive error message and the exit code.

    Example:
    >>> task_func("commands.csv", "/path/to/output_directory")
    ['/path/to/output_directory/command_1_output.txt', '/path/to/output_directory/command_2_output.txt', ...]
    """
'''

PROMPT_17 = """
def task_func(process_name: str) -> str:
    '''
    Check if a particular process is running based on its name. If it is not running, start it using the process name as a command. 
    If it is running, terminate the process and restart it by executing the process name as a command.

    Parameters:
    - process_name (str): The name of the process to check and manage. This should be executable as a command.

    Returns:
    - str: A message indicating the action taken:
        - "Process not found. Starting <process_name>."
        - "Process found. Restarting <process_name>."

    Requirements:
    - subprocess
    - psutil
    - time

    Example:
    >>> task_func('notepad')
    "Process not found. Starting notepad."
    OR
    >>> task_func('notepad')
    "Process found. Restarting notepad."
    '''
"""

def generate_specs(problems):
    """
    Function 1: Instructs the Reviewer Agent to generate and write specifications directly from the prompt.
    """
    for p in problems:
        pid = p['id']
        prompt_text = p['prompt']
        spec_file = p['spec_file']
        
        print(f"--- Generating Spec for Problem {pid} ---")
        
        # Use Reviewer Agent to generate and save directly
        reviewer_agent = Agent(agent_name="reviewer_agent")
        prompt = f"""
        Here is the problem description and function signature:
        {prompt_text}
        
        Please generate formal specifications (assertions) for this function.
        Ensure the specifications are correct (no self-reference, no side-effects).
        Then, SAVE the specifications to `{spec_file}` using `bash_command`.
        """
        reviewer_agent.run(prompt)
        print(f"Spec for Problem {pid} saved to {spec_file}\n")

def append_test_cases(problems):
    """
    Function 2: Instructs Test Gen Agent to read specs and append tests to the existing test file.
    """
    for p in problems:
        pid = p['id']
        test_file = p['test_file']
        spec_file = p['spec_file']
        
        print(f"--- Generating Tests for Problem {pid} ---")
        
        test_agent = Agent(agent_name="test_gen_agent")
        prompt_test = f"""
        Read the formal specifications from `{spec_file}`.
        Read the existing test file `{test_file}` to understand the context.
        Generate spec-guided test cases and APPEND them to `{test_file}`.
        Use `bash_command` to append the code.
        """
        test_agent.run(prompt_test)
        print(f"Tests for Problem {pid} appended to {test_file}\n")

if __name__ == "__main__":
    # Define the problems with explicit prompts and paths
    problems = [
        {
            "id": 15,
            "prompt": PROMPT_15,
            "test_file": os.path.abspath("problems_from_exercise2/test_BigCodeBench_15.py"),
            "spec_file": os.path.abspath("formal_specification/problem_15_spec.txt")
        },
        {
            "id": 17,
            "prompt": PROMPT_17,
            "test_file": os.path.abspath("problems_from_exercise2/test_BigCodeBench_17.py"),
            "spec_file": os.path.abspath("formal_specification/problem_17_spec.txt")
        }
    ]
    
    # Execute the workflow
    # generate_specs(problems)
    append_test_cases(problems)

