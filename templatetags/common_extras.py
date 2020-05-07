from django import template

register = template.Library()


@register.filter
def add_class(field, default_class):
    attrs = field.field.widget.attrs
    if attrs.get('class'):
        return field.as_widget()
    return field.as_widget(attrs={'class': default_class})
