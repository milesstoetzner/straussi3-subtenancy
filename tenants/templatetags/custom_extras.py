from django import template


register = template.Library()


@register.inclusion_tag('subtenancy/form_fields.html')
def form_fields(form, is_get):
    """
    Renders the fields of a form (label, widget, error or ok line, help text), see subtenancy/form_fields.html.
    If the request method is GET the form was not submitted yet, so no validation state is shown.
    """

    return {'form': form, 'is_get': is_get}


@register.filter(name='int_as_range')
def int_as_range(value):
    """
    Returns the list [value, value - 1, ..., 0]
    """

    return list(range(value, 0, -1))
