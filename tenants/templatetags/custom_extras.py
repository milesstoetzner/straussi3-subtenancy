from django import template


register = template.Library()


@register.inclusion_tag('subtenancy/bootstrap_form.html')
def bootstrap(form, is_get):
    """
    Adds bootstrap css to a given form. If the request method is GET, the validation is not displayed.
    """

    return {'form': form, 'is_get': is_get}


@register.filter(name='int_as_range')
def int_as_range(value):
    """
    Returns the list [value, value - 1, ..., 0]
    """

    return list(range(value, 0, -1))
