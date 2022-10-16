# Check if the file does not violate the requirements of the problem
# specification language. Specifically, no two entities in the same file
# can have the same name.
#
# @param: file_content A list of entities (employees or tasks) as parsed by the parser.
def validate_entities(entities):
    # extract the list of entity names
    names = [ e["name"] for e in entities ]
    # print(names)  # <- for debugging only

    if len(names) > len(set(names)):
        raise Exception("Invalid problem specification: entity names must be unique")


def validate_employees(employees):
    validate_entities(employees)


def validate_tasks(tasks):
    validate_entities(tasks)


# Check if the solution is valid, that is, if none of the constraints are violated.
# Here, the only constraint is that an employee can only be assigned to one task.
#
# @param solution - a set of (employee, task) pairs
def validate_solution(solution):
    # extract the list of employees used in the solution;
    # if the solution is invalid, the list will contain duplicates
    employees_used = [ item[0] for item in solution ]

    # when we transform the list into a set, the duplicates will be removed;
    # therefore, if there were duplicates to begin with, the size of the list
    # and the set will be different
    if len(employees_used) != len( set(employees_used) ):
        raise Exception("Solution invalid")
