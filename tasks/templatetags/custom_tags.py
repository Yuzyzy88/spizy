from django import template

register = template.Library()


@register.inclusion_tag("tasks/components/navbar.html", takes_context=True)
def navbar(context):
    request = context.get("request")

    return {
        "request": request,
    }


@register.inclusion_tag("tasks/components/footer.html", takes_context=True)
def footer(context):
    request = context.get("request")

    return {
        "request": request,
    }
