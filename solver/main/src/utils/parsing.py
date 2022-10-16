lowercase = { chr(x) for x in range(97, 123) }
uppercase = { chr(x) for x in range(65, 91) }
digits = { str(x) for x in range(0, 10) }
alphabet = lowercase.union(uppercase).union(digits)


# Parse name of an employee, task or a skill
# params file - contents of a file in a string format
# return (parsed name, rest of the file)
def parse_name(file):
    name = ""
    index = 0

    while ( index < len(file) ) and ( file[index] in alphabet ):
        name += file[index]
        index += 1

    if name == "":
        raise Exception("Parsing error: entity name cannot be empty")

    return (name, file[index:])


def parse_number(file):
    if len(file) == 0:
        raise Exception("Parsing error: expected a positive integer but found EOF")

    if file.startswith("0"):
        return ( 0, file[1:] )

    number_string = ""
    index = 0

    while ( index < len(file) ) and ( file[index] in digits ):
        number_string += file[index]
        index += 1

    if number_string == "":
        raise Exception('Parsing error: expected a positive integer but found "' + file[index] + '"')

    return ( int(number_string), file[index:] )


def parse_character(char, file):
    if len(char) != 1:  # check if only a single character was supplied, if not raise an exception
        raise Exception('Error in function parse_character: expected a single character but found ' + ( 'empty string' if len(char) == 0 else char ) )

    if len(file) == 0:
        raise Exception('Error parsing file: expected "' + char + '" but found EOF')

    if not file.startswith(char):
        raise Exception('Error parsing file: expected "' + char + '" but found "' + file[0] + '"')


def parse_skill(file):
    return parse_name(file)


# Parse a list of skills
# params file - contents of a file in a string format
def parse_skills(file):
    skill, rest_of_file = parse_skill(file)

    # if skill == "":
    #     return {}

    if ( len(rest_of_file) == 0 ) or ( not rest_of_file.startswith(",") ):
        return ( { skill }, rest_of_file )

    skills, rest_after_all_skills = parse_skills(rest_of_file[1:])

    return ( skills.union( { skill } ), rest_after_all_skills )


def parse_employee_name(file):
    return parse_name(file)


# params file - contents of a file in a string format
def parse_employee(file):
    # Q: Does case when file empty need to be handled?

    name, rest_after_name = parse_employee_name(file)

    parse_character("{", rest_after_name)

    skills, rest_after_skills = parse_skills(rest_after_name[1:])

    parse_character("}", rest_after_skills)

    employee = {
        "name": name,
        "skills": skills
    }

    return ( employee, rest_after_skills[1:])


def parse_task_name(file):
    return parse_name(file)


# params file - contents of a file in a string format
def parse_task(file):
    name, rest_after_name = parse_task_name(file)

    parse_character("[", rest_after_name)

    profit, rest_after_profit = parse_number(rest_after_name[1:])

    parse_character("]", rest_after_profit)

    parse_character("[", rest_after_profit[1:])

    loss, rest_after_loss = parse_number(rest_after_profit[2:])

    parse_character("]", rest_after_loss)

    parse_character("{", rest_after_loss[1:])

    skills, rest_after_skills = parse_skills(rest_after_loss[2:])

    parse_character("}", rest_after_skills)

    task = {
        "name": name,
        "profit": profit,
        "loss": loss,
        "skills": skills
    }

    return ( task, rest_after_skills[1:] )


def parse_item_list(file, item_parser):
    item, rest_of_file = item_parser(file)

    if len(rest_of_file) == 0:
        return [item]

    if not rest_of_file.startswith(","):
        raise Exception('Error parsing a file: expected "," but found "' + rest_of_file[0] + '"')

    return [item] + parse_item_list(rest_of_file[1:], item_parser)


# params file - contents of a file in a string format
def parse_employees(file):
    if len(file) == 0:
        return []

    return parse_item_list(file, parse_employee)


# params file - contents of a file in a string format
def parse_tasks(file):
    if len(file) == 0:
        return []

    return parse_item_list(file, parse_task)
