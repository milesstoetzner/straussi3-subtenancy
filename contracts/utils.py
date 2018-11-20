from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

# TODO: is this local?


def html_to_pdf(source, context):
    template = get_template(source)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    return result.getvalue()


def save_html_as_pdf(source, context, destination):
    pdf = html_to_pdf(source, context)
    try:
        file = open(destination, "w+b")
        file.write(pdf)
        file.close()
        return True
    except IOError:
        return False
