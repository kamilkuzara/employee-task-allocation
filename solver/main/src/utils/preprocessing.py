from pandas import DataFrame
import numpy as np


# Get the list of skills from a given list of entities.
#
# @param: entities A list of dictionaries, each specifying a single entity.
#                   Each dictionary must contain the key "skills" with a list of skills (of type string)
# @return: set of skills
def extract_skills_from_entities(entities):
    # extract the list of skills from each entity
    skills_list = [ e["skills"] for e in entities ]

    # flatten the list
    skills = [ item for sublist in skills_list for item in sublist ]

    return set(skills)


def extract_skills_from_problem(employees, tasks):
    employee_skills = extract_skills_from_entities(employees)
    task_skills = extract_skills_from_entities(tasks)

    all_skills = employee_skills.union(task_skills)

    return list(all_skills)


# Construct a pandas DataFrame from the given list of entities (employees or tasks).
#
# @param: entities A list of dictionaries, each specifying a single entity.
#                  Each dictionary must contain keys: "name" (value of type string),
#                                                      "skills" (a list of strings).
def construct_df(entities, skills):
    # construct rows
    rows = []
    for e in entities:
        name = e["name"]
        skills_encoding = [1 if s in e["skills"] else 0 for s in skills]
        rows.append( [ name, skills_encoding ] )

    rows = np.array(rows, dtype = "object")

    # transform the skill encodings into correct format for the data frame
    df_data = np.array([ np.array(x) for x in rows[:, 1] ])

    df = DataFrame( columns = skills, index = rows[:, 0], data = df_data )

    return df


def compute_gain_values(tasks):
    gains = {}
    for task in tasks:
        gains[task["name"]] = task["profit"] + task["loss"]

    return gains


def remove_unassignable(employees, tasks):
    employee_skills = extract_skills_from_entities(employees)   # get skills of all employees

    # filter out tasks that cannot be completed by any combination of employees
    tasks_filtered = [ t for t in tasks if t["skills"].issubset(employee_skills) ]

    task_skills = extract_skills_from_entities(tasks_filtered)  # get skills of the filtered tasks, i.e. those that can be completed

    # filter out the employees that cannot be assigned to any completable task
    employees_filtered = [ e for e in employees if not e["skills"].isdisjoint(task_skills) ]

    return ( employees_filtered, tasks_filtered )


def remove_redundant_skills(employees_df, tasks_df):
    # extract names of the skills not required by any task
    skills = (~tasks_df.any()).loc[ (~tasks_df.any()) != 0 ].index

    # drop columns with the redundant skills
    employees_df = employees_df.drop( skills, axis = 1 )
    tasks_df = tasks_df.drop( skills, axis = 1 )

    return ( employees_df, tasks_df )


def perform_preprocessing(employees, tasks):
    # 1. remove unassignable entities <- DONE
    #   (i.e. tasks that cannot be completed by any combination of employees
    #   and employees that cannot be assigned to any task)
    # 2. construct data frames for both employees and tasks <- DONE
    # 3. remove redundant skills <- DONE
    # 4. construct the (unordered) dictionary with task gain values <- DONE

    employees, tasks = remove_unassignable(employees, tasks)

    skills = extract_skills_from_problem(employees, tasks)

    employees_df = construct_df(employees, skills)
    tasks_df = construct_df(tasks, skills)

    employees_df, tasks_df = remove_redundant_skills(employees_df, tasks_df)

    gains = compute_gain_values(tasks)

    return ( employees_df, tasks_df, gains )
