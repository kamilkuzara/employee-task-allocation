def skills_to_string(skills):
    output = ""
    for s in skills:
        output += s + ", "

    return output[:len(output) - 2]

def employees_to_string(employees):
    output = ""
    for e in employees:
        output += "\t" + e["name"] + "{ " + skills_to_string(e["skills"]) + " }\n"

    return output

def tasks_to_string(tasks):
    output = ""
    for t in tasks:
        output += "\t" + t["name"] + "[" + str(t["profit"]) + "]" + "[" + str(t["loss"]) + "]" + "{ " + skills_to_string(t["skills"]) + " }\n"

    return output

def solution_to_string(solution):
    completed_tasks = { item[1] for item in solution }

    output = ""
    for task in completed_tasks:
        output += task + ":\n"
        assigned_employees = { item[0] for item in solution if item[1] == task }
        for employee in assigned_employees:
            output += "\t" + employee + "\n"

    return output
