# TEST CASES
import pytest
from unittest.mock import patch, MagicMock
import psutil
import sys
from pathlib import Path
import importlib
# prompt
"""
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
sys.path.insert(0, str(Path(__file__).parent.parent))

SOLUTION_MODULES = [
    "exercise2_part2_bcb_solutions.solution_minimax_m2_free_17"
]

def get_task_func(module_name):
    """Import and return task_func from module"""
    module = importlib.import_module(module_name)
    return module.task_func

@pytest.fixture(params=SOLUTION_MODULES, ids=lambda x: x.split('.')[-1])
def task_func(request):
    """Fixture that provides each solution's task_func"""
    return get_task_func(request.param)


@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_not_found_starts_process(mock_popen, mock_process_iter, task_func):
    # Simulating no running process
    mock_process_iter.return_value = []
    result = task_func('random_non_existent_process')
    assert result == "Process not found. Starting random_non_existent_process."
    mock_popen.assert_called_once_with('random_non_existent_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_found_restarts_process(mock_popen, mock_process_iter, task_func):
    # Simulating a running process
    process = MagicMock()
    process.name.return_value = 'notepad'
    mock_process_iter.return_value = [process]
    result = task_func('notepad')
    assert result == "Process found. Restarting notepad."
    # Expecting terminate called on the process and then restarted
    process.terminate.assert_called_once()
    mock_popen.assert_called_once_with('notepad')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_terminates_and_restarts_multiple_instances(mock_popen, mock_process_iter, task_func):
    # Simulating multiple instances of a running process
    process1 = MagicMock()
    process2 = MagicMock()
    process1.name.return_value = 'multi_instance'
    process2.name.return_value = 'multi_instance'
    mock_process_iter.return_value = [process1, process2]
    result = task_func('multi_instance')
    assert result == "Process found. Restarting multi_instance."
    process1.terminate.assert_called_once()
    process2.terminate.assert_called_once()
    mock_popen.assert_called_once_with('multi_instance')

# # ===== iteration 1 =====

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_raises_nosuchprocess_during_iteration(mock_popen, mock_process_iter, task_func):
    # Test to cover exception handling during process iteration
    # One process raises NoSuchProcess exception
    process1 = MagicMock()
    process1.name.side_effect = psutil.NoSuchProcess(pid=123)
    process2 = MagicMock()
    process2.name.return_value = 'other_process'
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('other_process')
    assert result == "Process not found. Starting other_process."
    mock_popen.assert_called_once_with('other_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_raises_accessdenied_during_iteration(mock_popen, mock_process_iter, task_func):
    # Test to cover AccessDenied exception during iteration
    process1 = MagicMock()
    process1.name.side_effect = psutil.AccessDenied(pid=123)
    process2 = MagicMock()
    process2.name.return_value = 'accessible_process'
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('accessible_process')
    assert result == "Process found. Restarting accessible_process."
    process2.terminate.assert_called_once()
    mock_popen.assert_called_once_with('accessible_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_raises_zombieprocess_during_iteration(mock_popen, mock_process_iter, task_func):
    # Test to cover ZombieProcess exception during iteration
    process1 = MagicMock()
    process1.name.side_effect = psutil.ZombieProcess(pid=123)
    process2 = MagicMock()
    process2.name.return_value = 'zombie_test'
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('zombie_test')
    assert result == "Process found. Restarting zombie_test."
    process2.terminate.assert_called_once()
    mock_popen.assert_called_once_with('zombie_test')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_multiple_exceptions_during_iteration(mock_popen, mock_process_iter, task_func):
    # Test to cover multiple different exceptions during iteration
    process1 = MagicMock()
    process1.name.side_effect = psutil.NoSuchProcess(pid=123)
    process2 = MagicMock()
    process2.name.side_effect = psutil.AccessDenied(pid=456)
    process3 = MagicMock()
    process3.name.side_effect = psutil.ZombieProcess(pid=789)
    process4 = MagicMock()
    process4.name.return_value = 'valid_process'
    mock_process_iter.return_value = [process1, process2, process3, process4]
    
    result = task_func('valid_process')
    assert result == "Process found. Restarting valid_process."
    process4.terminate.assert_called_once()
    mock_popen.assert_called_once_with('valid_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_raises_exception_during_termination(mock_popen, mock_process_iter, task_func):
    # Test to cover exception handling during process termination
    process1 = MagicMock()
    process1.name.return_value = 'test_process'
    process1.terminate.side_effect = psutil.AccessDenied(pid=123)
    mock_process_iter.return_value = [process1]
    
    result = task_func('test_process')
    assert result == "Process found. Restarting test_process."
    mock_popen.assert_called_once_with('test_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_mixed_exceptions_both_iteration_and_termination(mock_popen, mock_process_iter, task_func):
    # Test to cover exceptions during both iteration and termination
    process1 = MagicMock()
    process1.name.side_effect = psutil.NoSuchProcess(pid=111)
    process2 = MagicMock()
    process2.name.return_value = 'target_process'
    process2.terminate.side_effect = psutil.ZombieProcess(pid=222)
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('target_process')
    # Should still restart the process despite exceptions
    assert result == "Process found. Restarting target_process."
    mock_popen.assert_called_once_with('target_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_all_processes_raise_exceptions_during_iteration(mock_popen, mock_process_iter, task_func):
    # Test when all processes raise exceptions during iteration (no valid processes found)
    process1 = MagicMock()
    process1.name.side_effect = psutil.NoSuchProcess(pid=123)
    process2 = MagicMock()
    process2.name.side_effect = psutil.AccessDenied(pid=456)
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('nonexistent_process')
    # Should not find any process and should start it
    assert result == "Process not found. Starting nonexistent_process."
    mock_popen.assert_called_once_with('nonexistent_process')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_termination_with_multiple_exceptions(mock_popen, mock_process_iter, task_func):
    # Test termination of multiple processes where some raise exceptions
    process1 = MagicMock()
    process1.name.return_value = 'multi_proc'
    process1.terminate.side_effect = psutil.AccessDenied(pid=111)
    process2 = MagicMock()
    process2.name.return_value = 'multi_proc'
    process2.terminate.side_effect = psutil.NoSuchProcess(pid=222)
    process3 = MagicMock()
    process3.name.return_value = 'multi_proc'
    # This one succeeds
    process3.terminate.side_effect = None
    process3.terminate()
    
    mock_process_iter.return_value = [process1, process2, process3]
    
    result = task_func('multi_proc')
    assert result == "Process found. Restarting multi_proc."
    # All should have terminate called
    process1.terminate.assert_called_once()
    process2.terminate.assert_called_once()
    process3.terminate.assert_called_once()
    mock_popen.assert_called_once_with('multi_proc')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_wait_timeout_expired(mock_popen, mock_process_iter, task_func):
    # Test to cover proc.wait(timeout=5) raising TimeoutExpired (for solution_minimax_m2_free_17)
    process = MagicMock()
    process.name.return_value = 'wait_test_process'
    process.wait.side_effect = psutil.TimeoutExpired(5)
    process.kill = MagicMock()  # After timeout, kill should be called
    mock_process_iter.return_value = [process]
    
    result = task_func('wait_test_process')
    assert result == "Process found. Restarting wait_test_process."
    process.terminate.assert_called_once()
    process.kill.assert_called_once()  # kill should be called after timeout
    mock_popen.assert_called()

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_wait_succeeds(mock_popen, mock_process_iter, task_func):
    # Test to cover proc.wait(timeout=5) succeeding (for solution_minimax_m2_free_17)
    process = MagicMock()
    process.name.return_value = 'quick_terminate'
    process.wait.return_value = None  # Wait succeeds immediately
    process.kill = MagicMock()
    mock_process_iter.return_value = [process]
    
    result = task_func('quick_terminate')
    assert result == "Process found. Restarting quick_terminate."
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=5)
    mock_popen.assert_called()
    # kill should not be called if wait succeeds
    process.kill.assert_not_called()

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_terminated_during_wait(mock_popen, mock_process_iter, task_func):
    # Test to cover case where process is terminated during wait
    process = MagicMock()
    process.name.return_value = 'terminated_during_wait'
    process.wait.side_effect = psutil.NoSuchProcess(pid=123)  # Process dies during wait
    process.kill = MagicMock()
    mock_process_iter.return_value = [process]
    
    result = task_func('terminated_during_wait')
    assert result == "Process found. Restarting terminated_during_wait."
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=5)
    mock_popen.assert_called()

# ===== iteration 2 =====
@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_no_matching_process_found(mock_popen, mock_process_iter, task_func):
    # Test to cover case where processes exist but none match the target name
    process1 = MagicMock()
    process1.name.return_value = 'other_process_1'
    process2 = MagicMock()
    process2.name.return_value = 'other_process_2'
    mock_process_iter.return_value = [process1, process2]
    
    result = task_func('target_process')
    assert result == "Process not found. Starting target_process."
    mock_popen.assert_called_once_with('target_process')
    # No processes should be terminated
    process1.terminate.assert_not_called()
    process2.terminate.assert_not_called()

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_single_process_matching_multiple_times(mock_popen, mock_process_iter, task_func):
    # Test edge case where the same process is returned multiple times (shouldn't happen but good to test)
    process = MagicMock()
    process.name.return_value = 'duplicate_test'
    # Simulate the same process being seen twice
    mock_process_iter.return_value = [process, process]
    
    result = task_func('duplicate_test')
    assert result == "Process found. Restarting duplicate_test."
    # terminate should be called twice (once for each appearance)
    assert process.terminate.call_count == 2
    mock_popen.assert_called_once()

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_process_name_with_special_characters(mock_popen, mock_process_iter, task_func):
    # Test with a process name containing special characters
    process = MagicMock()
    process.name.return_value = 'test-process_v1.2'
    mock_process_iter.return_value = [process]
    
    result = task_func('test-process_v1.2')
    assert result == "Process found. Restarting test-process_v1.2."
    process.terminate.assert_called_once()
    mock_popen.assert_called_once_with('test-process_v1.2')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_terminate_then_start_same_process(mock_popen, mock_process_iter, task_func):
    # Test to ensure the process is started after termination
    process = MagicMock()
    process.name.return_value = 'restart_test'
    mock_process_iter.return_value = [process]
    
    result = task_func('restart_test')
    
    # Verify terminate was called
    process.terminate.assert_called_once()
    # Verify Popen was called (process was restarted)
    assert mock_popen.call_count == 1
    mock_popen.assert_called_with('restart_test')

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_no_process_iteration_results(mock_popen, mock_process_iter, task_func):
    # Test when process_iter returns an empty iterator
    mock_process_iter.return_value = iter([])  # Empty iterator
    
    result = task_func('nonexistent')
    assert result == "Process not found. Starting nonexistent."
    mock_popen.assert_called_once_with('nonexistent')




# ===== SPEC-GUIDED TESTS =====
# These tests directly verify the formal specifications from problem_17_spec.txt

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_return_type_string(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check return type - ensures function returns string as specified in function signature"""
    mock_process_iter.return_value = []
    result = task_func('test_process')
    assert isinstance(result, str), f"Expected str, got {type(result)}"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_return_value_format_process_not_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check return value format - result must match expected message pattern for 'not found' case"""
    mock_process_iter.return_value = []
    process_name = 'nonexistent_process'
    result = task_func(process_name)
    expected = f"Process not found. Starting {process_name}."
    assert result == expected, f"Expected '{expected}', got '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_return_value_format_process_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check return value format - result must match expected message pattern for 'found' case"""
    process = MagicMock()
    process.name.return_value = 'existing_process'
    mock_process_iter.return_value = [process]
    process_name = 'existing_process'
    result = task_func(process_name)
    expected = f"Process found. Restarting {process_name}."
    assert result == expected, f"Expected '{expected}', got '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_process_name_preservation_not_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check process name preservation - input process_name must appear in return message (not found case)"""
    process_name = 'my_special_process'
    mock_process_iter.return_value = []
    result = task_func(process_name)
    assert process_name in result, f"Process name '{process_name}' not found in result: '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_process_name_preservation_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check process name preservation - input process_name must appear in return message (found case)"""
    process_name = 'another_special_process'
    process = MagicMock()
    process.name.return_value = process_name
    mock_process_iter.return_value = [process]
    result = task_func(process_name)
    assert process_name in result, f"Process name '{process_name}' not found in result: '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_message_structure_not_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check message structure - return string must contain required keywords for 'not found' case"""
    mock_process_iter.return_value = []
    result = task_func('test_process')
    assert ("Process" in result and "not found" in result and "Starting" in result), \
        f"Required keywords not found in result: '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_message_structure_found(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check message structure - return string must contain required keywords for 'found' case"""
    process = MagicMock()
    process.name.return_value = 'test_process'
    mock_process_iter.return_value = [process]
    result = task_func('test_process')
    assert ("Process" in result and "found" in result and "Restarting" in result), \
        f"Required keywords not found in result: '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_message_completeness_ends_with_period(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Check message completeness - return string should be properly formatted with ending period"""
    # Test for not found case
    mock_process_iter.return_value = []
    result1 = task_func('process1')
    assert result1.endswith("."), f"Not found case result doesn't end with period: '{result1}'"
    
    # Test for found case
    process = MagicMock()
    process.name.return_value = 'process2'
    mock_process_iter.return_value = [process]
    result2 = task_func('process2')
    assert result2.endswith("."), f"Found case result doesn't end with period: '{result2}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_comprehensive_all_assertions(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Comprehensive test that verifies all formal specification assertions together"""
    process_name = 'comprehensive_test'
    
    # Test not found case with all specifications
    mock_process_iter.return_value = []
    result = task_func(process_name)
    
    # Check all assertions for not found case
    assert isinstance(result, str)
    expected_not_found = f"Process not found. Starting {process_name}."
    assert result == expected_not_found
    assert process_name in result
    assert ("Process" in result and "not found" in result and "Starting" in result)
    assert result.endswith(".")
    
    # Test found case with all specifications
    process = MagicMock()
    process.name.return_value = process_name
    mock_process_iter.return_value = [process]
    result = task_func(process_name)
    
    # Check all assertions for found case
    assert isinstance(result, str)
    expected_found = f"Process found. Restarting {process_name}."
    assert result == expected_found
    assert process_name in result
    assert ("Process" in result and "found" in result and "Restarting" in result)
    assert result.endswith(".")

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_exact_message_patterns_only(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Verify that return values match ONLY the two expected patterns exactly"""
    # Test various process names to ensure only exact patterns are returned
    test_names = ['test', 'process.exe', 'my_app_v2.1', 'special-process_name']
    
    for process_name in test_names:
        # Test not found case
        mock_process_iter.return_value = []
        result = task_func(process_name)
        valid_not_found = f"Process not found. Starting {process_name}."
        assert result == valid_not_found, f"Invalid pattern for not found case: '{result}'"
        
        # Test found case
        process = MagicMock()
        process.name.return_value = process_name
        mock_process_iter.return_value = [process]
        result = task_func(process_name)
        valid_found = f"Process found. Restarting {process_name}."
        assert result == valid_found, f"Invalid pattern for found case: '{result}'"

@patch('psutil.process_iter')
@patch('subprocess.Popen')
def test_spec_alternate_pattern_rejection(mock_popen, mock_process_iter, task_func):
    """Spec-guided test: Verify that function rejects non-standard message patterns"""
    process = MagicMock()
    process.name.return_value = 'test_process'
    mock_process_iter.return_value = [process]
    
    result = task_func('test_process')
    
    # Verify it's exactly one of the two valid patterns, not variations
    valid_patterns = [
        "Process found. Restarting test_process.",
        "Process not found. Starting test_process."
    ]
    
    # Reject common variations that should not occur
    invalid_variations = [
        "Process test_process found. Restarting.",
        "Found process test_process. Restarting test_process.",
        "Process found test_process. Restarting.",
        "Process found: test_process (restarting).",
        "Process found - restarting test_process",
        "test_process process found, restarting"
    ]
    
    assert result in valid_patterns, f"Result '{result}' not in valid patterns"
    assert result not in invalid_variations, f"Result '{result}' matches invalid variation"
