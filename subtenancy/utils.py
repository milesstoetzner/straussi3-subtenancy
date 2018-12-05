def get_verbose_changed_data(changed_data, model):
    """
    Returns the verbose names of the changed fields of a form
    """

    changes = []
    for field in changed_data:
        changes.append(model._meta.get_field(field).verbose_name)
    return changes
