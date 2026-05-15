import pytest
from htn_engine import HTNPlanner
from htn_domains import get_mystery_domain

import htn_monitor
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_htn_monitor_verification():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"accomplished": true, "explanation": "Task done"}'
        
        success, reason = await htn_monitor.verify_task_completion("Find clue", "I found a map.")
        assert success is True
        assert reason == "Task done"

def test_planner_basic_solve():
    p = HTNPlanner()
    
    def op_a(state):
        state['a'] = True
        return state
    def op_b(state):
        state['b'] = True
        return state
    
    p.declare_operator('op_a', op_a)
    p.declare_operator('op_b', op_b)
    
    def method_c(state):
        return ['op_a', 'op_b']
    
    p.declare_method('compound', method_c)
    
    plan = p.solve({}, ['compound'])
    assert plan == ['op_a', 'op_b']

def test_planner_precondition_failure():
    p = HTNPlanner()
    
    def op_fail(state):
        if state.get('possible'):
            return state
        return None
    
    p.declare_operator('op_fail', op_fail)
    
    plan = p.solve({'possible': False}, ['op_fail'])
    assert plan is None

def test_mystery_domain_full_solve():
    p = get_mystery_domain()
    # If suspect is present, we should be able to solve
    plan = p.solve({'suspect_present': True}, ['solve_mystery'])
    assert len(plan) == 4
    assert plan[-1] == 'trigger_arrest'

def test_mystery_domain_interrogation_failure():
    p = get_mystery_domain()
    # No suspect present -> interrogation fails -> solve_mystery fails
    plan = p.solve({'suspect_present': False}, ['solve_mystery'])
    assert plan is None
