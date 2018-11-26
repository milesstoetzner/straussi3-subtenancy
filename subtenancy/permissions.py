def is_assistant(user):
    return user.is_assistant


def is_external(user):
    return user.is_external


def is_assistant_or_external(user):
    return user.is_assistant or user.is_external


def is_subtenant(user):
    return user.is_subtenant


def is_maintenant(user):
    return user.is_maintenant


def is_tenant(user):
    return user.is_maintenant or user.is_subtenant
