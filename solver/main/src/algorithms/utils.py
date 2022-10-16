import numpy as np

# Get the employees that can be assigned to a task, or the tasks that an employee can be assigned to.
# Note, for an entity of one type (e.g. employee), we want to get assignable entities of the other type (e.g. tasks).
#
# @return entities_df with unassignable entities filtered out
def get_assignable(entity, entities_df):
    # the mask performs a logical AND on the skill encodings of an item (from entities_df) and the given entity;
    # as a result, only the skills that both appear in the entity as well as in the item
    # are given the value of 1 in the resulting row; the rest are set to 0
    mask = lambda item: np.logical_and(item, entity)

    # apply the above mask to all entities
    entities_filtered = entities_df.apply( mask, axis = 1 ).astype(int)

    # remove unassignable entities, i.e. remove rows with all zeros
    assignable = entities_filtered[ entities_filtered.any(axis = 1) ]

    return entities_df.loc[ assignable.index ]


def is_completed_by(task, employees):
    # get skills offered collectively by the employees
    offered_skills = employees.any().astype(int)

    # perform a logical AND to find the common skills, i.e. those that are both
    # required by the task and offered by the employees
    common_skills = np.logical_and(task, offered_skills).astype(int)

    # the list of common skills should match exactly the list of skills of the task
    if task[ task != common_skills ].empty:
        return True
    else:
        return False
