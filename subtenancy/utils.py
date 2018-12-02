def is_assistant(user):
    """
    Returns if a given user is an assistant
    """

    return user.is_assistant


def is_external(user):
    """
    Returns if a given user is an external - e.g. SWS or janitor
    """

    return user.is_external


def is_assistant_or_external(user):
    """
    Returns if a given user is an assistant or an external
    """

    return user.is_assistant or user.is_external


def is_subtenant(user):
    """
    Returns if a given user is a subtenant
    """

    return user.is_subtenant


def is_maintenant(user):
    """
    Returns if a given user is a maintenant
    """

    return user.is_maintenant


def is_tenant(user):
    """
    Returns if a given user is a maintenant or subtenant
    """

    return user.is_maintenant or user.is_subtenant


def get_verbose_changed_data(changed_data, model):
    """
    Returns the verbose names of the changed fields of a form
    """

    changes = []
    for field in changed_data:
        changes.append(model._meta.get_field(field).verbose_name)
    return changes
