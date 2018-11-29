from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import timedelta, datetime

# TODO: is this local?


def html_to_pdf(source, context):
    template = get_template(source)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
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


# credits to Andreas Balogh
def add_one_month(dt0):
    dt1 = dt0.replace(day=1)
    dt2 = dt1 + timedelta(days=32)
    dt3 = dt2.replace(day=1)
    return dt3


# credits to Augusto Men
def is_end_of_month(d):
    next_month = d.replace(day=28) + timedelta(days=4)
    return d == next_month - timedelta(days=next_month.day)
