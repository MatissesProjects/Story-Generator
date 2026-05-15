import copy

class HTNPlanner:
    """
    A simple Hierarchical Task Network (HTN) planner for narrative orchestration.
    Decomposes high-level narrative goals into primitive operators.
    """
    def __init__(self):
        self.methods = {}
        self.operators = {}

    def declare_method(self, task_name, method_func):
        """Registers a method for a compound task."""
        if task_name not in self.methods:
            self.methods[task_name] = []
        self.methods[task_name].append(method_func)

    def declare_operator(self, task_name, operator_func):
        """Registers a primitive operator."""
        self.operators[task_name] = operator_func

    def solve(self, state, tasks):
        """
        Tries to find a sequence of operators that satisfies the task list.
        Returns a list of operators or None.
        """
        if not tasks:
            return []

        task = tasks[0]
        remaining_tasks = tasks[1:]

        # Case 1: Primitive Task (Operator)
        if task in self.operators:
            operator = self.operators[task]
            new_state = operator(copy.deepcopy(state))
            if new_state is not None:
                plan = self.solve(new_state, remaining_tasks)
                if plan is not None:
                    return [task] + plan

        # Case 2: Compound Task (Method)
        elif task in self.methods:
            for method in self.methods[task]:
                subtasks = method(state)
                if subtasks is not None:
                    plan = self.solve(state, subtasks + remaining_tasks)
                    if plan is not None:
                        return plan

        return None

# --- Example Domain (for testing) ---

def example_domain_setup(planner):
    # Operators
    def op_move_to_tavern(state):
        state['at_tavern'] = True
        return state

    def op_buy_drink(state):
        if state.get('at_tavern') and state.get('gold', 0) >= 5:
            state['gold'] -= 5
            state['has_drink'] = True
            return state
        return None

    planner.declare_operator('move_to_tavern', op_move_to_tavern)
    planner.declare_operator('buy_drink', op_buy_drink)

    # Methods
    def method_get_info_rich(state):
        if state.get('gold', 0) >= 5:
            return ['move_to_tavern', 'buy_drink']
        return None

    planner.declare_method('get_info', method_get_info_rich)

if __name__ == "__main__":
    p = HTNPlanner()
    example_domain_setup(p)
    
    initial_state = {'gold': 10, 'at_tavern': False}
    result = p.solve(initial_state, ['get_info'])
    print(f"Plan: {result}")
