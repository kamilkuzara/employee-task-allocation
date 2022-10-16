import time
import numpy as np
from .utils import get_assignable, is_completed_by


def compute_supply_demand_ratio(employees_df, tasks_df):
    # compute supply
    supply = employees_df.sum()

    # compute demand
    demand = tasks_df.sum()

    supply_demand_ratio = supply / demand

    return supply_demand_ratio


# Returns an UNSORTED list of (task, h_value) pairs
def compute_h_values(employees_df, tasks_df, gains):
    # compute the supply and the demand for each skill
    supply_demand_ratio = compute_supply_demand_ratio(employees_df, tasks_df)

    # compute the heuristic values for each task
    h_values = []
    for task_name, g in gains.items():
        # get skill encoding for the task, i.e. a pandas Series specifying
        # for each skill whether it is required by the task
        task = tasks_df.loc[ task_name ]

        t_skill_names = task[ task != 0 ].index   # get the names of skills of the task, i.e. those required by the task

        # compute the heuristic value for the task as the product of the task's gain and the supply/demand
        # ratios for the skills required by the task
        skills_product = supply_demand_ratio.loc[ t_skill_names ].product()
        h = g * skills_product

        h_values.append( (task_name, h) )

    return h_values


# @return ( next_employee_name, assignable ) - where next_employee_name is the name of the employee
#                                              chosen to be assigned to the task, and assignable is an
#                                              updated dataframe
def get_next_employee(assignable):

    # get the names of the skills offered by the least number of employees;
    # these are the most-constraining variables as they are the hardest to satisfy
    # and may impose that certain employees have to be chosen for assignment,
    # e.g. if a skill is only offered by one employee, then in order to complete
    # the task this employee will HAVE TO be assigned to this task
    supply = assignable.sum()
    mcv_skills = supply[ supply == supply.min() ].index

    # get the names of the employees that satisfy at least one of the mcv skills
    mcv_employee_names = assignable[mcv_skills][ assignable[mcv_skills].any(axis = 1) ].index

    # get the mcv employees from the original "assignable" table,
    # note: all task-relevant skills are present in the resultant dataframe and not just the mcv ones
    mcv_employees = assignable.loc[ mcv_employee_names ]

    # out of those that satisy the mcv skills, get the employees that satisfy the most skills generally for the task
    best_employees = mcv_employees[ mcv_employees.sum(axis = 1) == mcv_employees.sum(axis = 1).max() ]

    # choose a random employee from those above and get the name of that employee;
    # this is the employee that is chosen for assignment
    next_employee_name = best_employees.sample( n = 1 ).index[0]
    next_employee = assignable.loc[ next_employee_name ]

    # remove the skills of that employee from the dataframe
    assignable = assignable.drop( next_employee[ next_employee != 0 ].index , axis = 1 )

    # remove the employee from the dataframe
    assignable = assignable.drop( next_employee_name, axis = 0 )

    return next_employee_name, assignable


def greedy_heuristic(employees_df, tasks_df, gains):
    # compute heuristic values for all tasks
    h_values = compute_h_values(employees_df, tasks_df, gains)

    # sort the tasks according to the heuristic values
    tasks_sorted = sorted( h_values, key = lambda item: item[1], reverse = True )

    completed = set()
    solution = set()
    total_gain = 0
    while len(tasks_sorted) > 0:
        # remove the first item from the list of sorted (task, h_value) pairs and get the task name
        task_name = tasks_sorted.pop(0)[0]
        task = tasks_df.loc[ task_name ]

        # get the subset of employees assignable to the task;
        # returned as a pandas DataFrame with unassignable employees (rows) removed
        assignable = get_assignable( task, employees_df )

        # first, check if the task can at all be completed by the available employees
        if not is_completed_by( task, assignable ):
            continue

        # remove irrelevant skills, i.e. those not required by the task
        # get_next_employee(...) needs this step to execute correctly
        assignable = assignable[ task[task != 0].index ]

        employees_used = set()
        assignment = set()
        while ( not assignable.empty ) and ( task_name not in completed ):
            # get the next employee to assign to the task and an updated table of assignable employees
            e_next, assignable = get_next_employee(assignable)
            # print(task_name + " - " + e_next)
            employees_used.add(e_next)
            assignment.add( (e_next, task_name) )

            if is_completed_by( task, employees_df.loc[ employees_used ] ):
                completed.add(task_name)

        if task_name in completed:
            solution.update(assignment)     # add the assignment to the solution
            employees_df = employees_df.drop( employees_used, axis = 0 )
            total_gain += gains[task_name]

    return ( solution, total_gain )


def greedy_heuristic_solver(employees_df, tasks_df, gains):
    start_time = time.time()
    solution, total_gain = greedy_heuristic(employees_df, tasks_df, gains)
    end_time = time.time()

    result = {
        "solution": solution,
        "total gain": total_gain,
        "running time": end_time - start_time
    }

    return result
