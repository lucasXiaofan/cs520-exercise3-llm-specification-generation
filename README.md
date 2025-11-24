# CS520 Exercise 3: LLM Specification Generation
Author: XiaoFan Lu
## Code Structure
- **`agent/`**: Contains the `agent.py` script and `agent.yaml` configuration used to generate specifications and tests.
- **`formal_specification/`**: Stores the generated formal specifications (assertions) for Problems 15 and 17.
- **`problems_from_exercise2/`**: Contains the test files (`test_BigCodeBench_15.py`, `test_BigCodeBench_17.py`). These include both the original tests and the new **SPEC-GUIDED TESTS** appended by the agent.
- **`exercise2_part2_bcb_solutions/`**: The solution code for the problems.
- **`report.md`**: Detailed analysis of the accuracy and coverage results.

## How to View Results
To view the coverage reports, please open the following `index.html` files in your browser:

### Problem 15 (Command Execution)
- **Baseline**: `bcbp15_no_spec_html/index.html`
- **With Specs**: `bcbp15_has_spec_html/index.html`

### Problem 17 (Process Management)
- **Baseline**: `bcbp17_no_spec_html/index.html`
- **With Specs**: `bcbp17_has_spec_html/index.html`