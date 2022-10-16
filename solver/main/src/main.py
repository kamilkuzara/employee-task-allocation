#!/usr/bin/env python3

import sys
import utils
import algorithms

def get_help():
    help_text = "Usage: python3 main.py  <algorithm_code>  <employees_file>  <tasks_file>  [solution_file]\n\n"
    help_text += "Available algorithms:\n"

    for algorithm_code, algorithm in algorithms.algorithms.items():
        help_text += "\t" + algorithm_code + " - " + algorithm.get("description", "No description provided") + "\n"

    return help_text

# #######################################################################
# The function parses command line parameters. It expects to receive an array
# where each item is a parameter. The 0-th item is the name of the program followed
# by parameters specified in the command line.
#
def parse_args(argv):

    # array cannot be empty
    if len(argv) == 0:
        raise Exception("Incorrect number of parameters\n" + get_help())

    # the user did not provide any parameters
    if len(argv) == 1:
        raise Exception(get_help())

    # the user specified some params but not enough to continue execution
    if len(argv) < 4:
        raise Exception("Parameters missing\n" + get_help())

    # if we get here, required no. of params satisfied

    # parse algorithm code
    algo = argv[1]
    if algo not in algorithms.algorithms:
        raise Exception("Incorrect algorithm code\n" + get_help())

    params = {
        "algorithm": algo,
        "employees_path": argv[2],
        "tasks_path": argv[3]
    }

    # parse optional arguments if provided
    if len(argv) == 5:
        params["solution_path"] = argv[4]

    return params

# #######################################################################
# Open a file and return its contents in a string format
#
def open_file(path):
    try:
        file = open(path)
        file_content = file.read()
        file.close()
        return file_content
    except FileNotFoundError as e:
        raise Exception(e)

def main():
    # 1. parse arguments from the command line <- DONE
    # 2. open employees file <- DONE
    # 3. open tasks file <- DONE
    # 4. parse employees file <- DONE
    # 5. parse tasks file <- DONE
    # 6. validate input data (e.g. no two employees can have the same name, etc.) <- DONE
    # 7. preprocess the data <- DONE
    #   ( i.e. create appropriate data structs for algorithms,
    #   remove tasks and employees that cannot be matched with anyone )
    # 8. call chosen algorithm with parsed files as args    <- DONE
    # 9. validate the solution  <- DONE
    # 10. compute the net profit
    # 11. (optional) save solution to a file
    try:
        args = parse_args(sys.argv)

        # open files and get their contents in string format
        employees_file = open_file(args["employees_path"])
        tasks_file = open_file(args["tasks_path"])

        # remove all whitespaces
        employees_file = "".join(employees_file.split())
        tasks_file = "".join(tasks_file.split())

        # parse and validate employees
        print("Parsing employees file...\t", end = "")
        employees = utils.parse_employees(employees_file)
        print("Done")
        print("Validating the employees...\t", end = "")
        utils.validate_employees(employees)
        print("Done (employees specification valid)")
        print(utils.employees_to_string(employees))

        # parse and validate tasks
        print("Parsing tasks file...\t", end = "")
        tasks = utils.parse_tasks(tasks_file)
        print("Done")
        print("Validating the tasks...\t", end = "")
        utils.validate_tasks(tasks)
        print("Done (tasks specification valid)")
        print(utils.tasks_to_string(tasks))

        # create appropriate data structures from the parsed problem instance
        print("Performing preprocessing...\t", end = "")
        employees_df, tasks_df, gains = utils.perform_preprocessing(employees, tasks)
        print("Done")
        print(employees_df)
        print(tasks_df)
        print(gains)

        # solve the problem instance
        print("\nRunning " + algorithms.algorithms[ args["algorithm"] ]["description"] + "...\t", end = "")
        result = algorithms.algorithms[ args["algorithm"] ][ "algorithm" ](employees_df, tasks_df, gains)
        print("Done (solution found)")

        # validate the solution; if invalid, an exception will be raised
        print("Validating the solution...\t", end = "")
        utils.validate_solution( result["solution"] )
        print("Done (solution valid)")

        # if we get here, the solution is valid

        # print out the solution
        print("Solution:\n")
        print( utils.solution_to_string( result["solution"] ) )

        # compute the statistics
        net_profit = utils.compute_net_profit( [ task for task in tasks if task["name"] in tasks_df.index ], result["total gain"] )

        # print out the statistics
        print("Total gain: " + str(result["total gain"]) )
        print("Net profit: " + str(net_profit) )
        print("Running time: " + str( round(result["running time"], 5) ) + "sec")

    except Exception as e:
        print("\n")
        print(e)

if __name__ == '__main__':
    main()
