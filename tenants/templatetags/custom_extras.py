from django import template


register = template.Library()


@register.inclusion_tag('subtenancy/bootstrap_form.html')
def bootstrap(form, is_get):
    return {'form': form, 'is_get': is_get}


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='int_as_range')
def int_as_range(value):
    return list(range(value, 0, -1))
