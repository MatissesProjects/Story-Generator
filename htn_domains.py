from htn_engine import HTNPlanner

def get_mystery_domain():
    planner = HTNPlanner()

    # --- Operators (Primitive Tasks) ---
    
    def op_detective_arrival(state):
        state['at_scene'] = True
        return state
        
    def op_search_for_prints(state):
        if state.get('at_scene'):
            state['has_fingerprints'] = True
            return state
        return None
        
    def op_interrogate_suspect(state):
        if state.get('has_fingerprints') and state.get('suspect_present'):
            state['has_confession'] = True
            return state
        return None

    def op_trigger_arrest(state):
        if state.get('has_confession'):
            state['mystery_solved'] = True
            return state
        return None

    planner.declare_operator('detective_arrival', op_detective_arrival)
    planner.declare_operator('search_for_prints', op_search_for_prints)
    planner.declare_operator('interrogate_suspect', op_interrogate_suspect)
    planner.declare_operator('trigger_arrest', op_trigger_arrest)

    # --- Methods (Compound Tasks) ---

    def method_solve_standard(state):
        return ['detective_arrival', 'search_for_prints', 'interrogate_suspect', 'trigger_arrest']

    planner.declare_method('solve_mystery', method_solve_standard)

    return planner

if __name__ == "__main__":
    mystery_p = get_mystery_domain()
    
    # World state: Suspect is already there
    initial_state = {'suspect_present': True}
    plan = mystery_p.solve(initial_state, ['solve_mystery'])
    print(f"Mystery Plan: {plan}")
