import time
import math
import random
from .utils import get_assignable, is_completed_by


hyperparameters = {
    "n_change_parameter": 2,
    "initial_probability_threshold": 0.95,
    "alpha": 0.75,   # rate of change for temperature, should be within range (0.8, 0.99)
    "beta": 1.05,    # rate of change for phase length, should be > 1
    "min_temp": 5,   # termination criterion, we stop the search when the temperature gets below this value
    "initial_phase_length": 10
}


# def greedy_heuristic_init(employees_df, tasks_df, gains):
#     pass


def compute_cost(config, employees_df, tasks_df, gains):
    # get the set of tasks present in the configuration
    assigned_tasks = { item[1] for item in config }

    # for each of the above tasks, check if its completed by the configuration
    # if yes, add its gain to the cost
    cost = 0
    for task_name in assigned_tasks:
        # get employees assigned to the task
        assigned_employees = { item[0] for item in config if item[1] == task_name }

        if is_completed_by( tasks_df.loc[task_name], employees_df.loc[assigned_employees] ):
            cost += gains[task_name]

    return cost


# Generate a random initial solution/configuration and compute its cost. Note,the function generates
# a complete configuration, i.e. one where every employee is assigned to some task.
#
# @return config, cost - where config is the initial solution and cost is its cost represented by the total gain
def random_init(employees_df, tasks_df, gains):
    # generate the configuration
    config = set()
    for employee_name, employee in employees_df.iterrows():
        # sample a random task from those assignable to the employee
        task_name = get_assignable(employee, tasks_df).sample( n = 1 ).index[0]

        # assign the employee to the sampled task
        config.add( (employee_name, task_name) )

    # compute the cost of the configuration
    cost = compute_cost(config, employees_df, tasks_df, gains)

    return config, cost


def n_change(employees_df, tasks_df, n = 1):
    # the number of employees is the upper limit on the number of changes
    # we can make so check if this requirement is not violated, otherwise raise an exception
    if n > len(employees_df.index):
        raise Exception("Simulated Annealing Error: n-change parameter cannot be larger than the number of employees")

    additions = set()   # assignments that will be added to the solution in place of the old ones

    # sample n random employees
    employees_to_update = employees_df.sample( n = n )

    # for each of the n employees, sample a random task from those that the employee can be assigned to
    for employee_name, employee in employees_to_update.iterrows():
        task_name = get_assignable(employee, tasks_df).sample( n = 1 ).index[0]

        additions.add( (employee_name, task_name) )

    return additions


def compute_cost_difference(old_config, additions, deletions, employees_df, tasks_df, gains):
    # get the tasks that are updated as a result of the change
    tasks_updated = { item[1] for item in additions }.union({ item[1] for item in deletions })

    # for each of the updated tasks, decide whether it became completed or uncompleted in the new solution
    cost_difference = 0
    for task_name in tasks_updated:
        # get employees added to the task in the new solution
        employee_additions = { item[0] for item in additions if item[1] == task_name }

        # get the employees removed from the task in the new solution
        employee_deletions = { item[0] for item in deletions if item[1] == task_name }

        # get all the employees assigned to the task in the old solution
        old_task_assignment = { item[0] for item in old_config if item[1] == task_name }

        # generate the set of employees assigned to the task in the new solution, i.e. update the assignment for the task
        new_task_assignment = old_task_assignment.union(employee_additions).difference(employee_deletions)

        # decide whether the task was completed in the old and new solutions
        was_completed = is_completed_by( tasks_df.loc[task_name], employees_df.loc[old_task_assignment] )
        is_completed = is_completed_by( tasks_df.loc[task_name], employees_df.loc[new_task_assignment] )

        if was_completed and not is_completed:
            cost_difference -= gains[task_name]
        elif not was_completed and is_completed:
            cost_difference += gains[task_name]

    return cost_difference


def generate_neighbour(current_config, current_cost, employees_df, tasks_df, gains):
    additions = n_change(employees_df, tasks_df, hyperparameters["n_change_parameter"])
    employees_to_update = { item[0] for item in additions }
    deletions = { item for item in current_config if item[0] in employees_to_update }

    # get rid of the intersection between the additions and deletions; these are the
    # assignments that remain unchanged
    intersection = additions.intersection(deletions)
    additions = additions.difference(intersection)
    deletions = deletions.difference(intersection)

    # compute the cost of the new solution based on the old solution and the updates
    new_cost = current_cost + compute_cost_difference(current_config, additions, deletions, employees_df, tasks_df, gains)

    # generate the new solution
    new_config = current_config.union(additions).difference(deletions)

    return new_config, new_cost


# Compute the initial temperature such that the probability for accepting all neighbours
# is at or above a certain level speciied as "initial_probability_threshold" in the hyperparameters dict.
#
# Note, that the neighbours with the maximal negative difference of cost to the current solution will be
# the least likely to be accepted. As such, to make sure that all neighbours of the initial solution will
# be accepted with a given threshold probability, we need to compute the temperature for the maximum possible
# difference. This difference is calculated as the sum of n tasks with the highest gain values, where n is the
# hyperparameter of the neighbour generation function.
#
# @return initial temperature that accepts all neighbours with at least the threshold probability
def compute_initial_temp(gains):
    gains_sorted = sorted( list(gains.items()), key = lambda item: item[1], reverse = True )

    max_difference = sum( { item[1] for item in gains_sorted[ 0 : hyperparameters["n_change_parameter"] ] } )

    return -1 * max_difference / math.log( hyperparameters["initial_probability_threshold"] )


def update_temp(temp):
    return hyperparameters["alpha"] * temp


def update_phase_length(phase_length):
    return math.ceil( hyperparameters["beta"] * phase_length )


# def compute_initial_phase_length():
#     pass


def simulated_annealing(employees_df, tasks_df, gains, initialisation = random_init):
    # compute the initial solution/configuration and its cost using the specified function
    current_config, current_cost = initialisation(employees_df, tasks_df, gains)
    best_config = current_config
    best_cost = current_cost

    phase_length = hyperparameters["initial_phase_length"]
    temp = compute_initial_temp(gains)

    finished = False
    while not finished:
        for i in range(phase_length):
            new_config, new_cost = generate_neighbour(current_config, current_cost, employees_df, tasks_df, gains)

            if new_cost > current_cost: # remember, higher cost is better
                # accept the new configuration, i.e. move to this solution
                current_config = new_config
                current_cost = new_cost
                if new_cost > best_cost:    # if also the best config yet, update the best
                    best_config = new_config
                    best_cost = new_cost
            # else (if new config is worse than current config), accept with certain probability
            elif math.exp( (new_cost - current_cost) / temp ) >= random.random():
                current_config = new_config
                current_cost = new_cost

        phase_length = update_phase_length(phase_length)
        temp = update_temp(temp)

        if temp < hyperparameters["min_temp"]:  # stopping criterion for the search
            finished = True

    return best_config, best_cost


def simulated_annealing_with_random(employees_df, tasks_df, gains):
    start_time = time.time()
    # perform Simulated Annealing with random initialisation
    solution, total_gain = simulated_annealing(employees_df, tasks_df, gains)
    end_time = time.time()

    result = {
        "solution": solution,
        "total gain": total_gain,
        "running time": end_time - start_time
    }

    return result


# def simulated_annealing_with_gh(employees_df, tasks_df, gains):
#     pass
