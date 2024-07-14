"""
from django_tex.core import compile_template_to_pdf


def save_html_as_pdf(source, context, destination):
    pdf = html_to_pdf(source, context)
    file = open(destination, "w+b")
    file.write(pdf)
    file.close()


def html_to_pdf(template_name, context):
    return compile_template_to_pdf(template_name, context)
"""

import os
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa


def link_callback(uri, rel):
    return os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))


def html_to_pdf(source, context):
    template = get_template(source)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, link_callback=link_callback, encoding='UTF-8')
    return result.getvalue()


def save_html_as_pdf(source, context, destination):
    pdf = html_to_pdf(source, context)
    file = open(destination, "w+b")
    file.write(pdf)
    file.close()


HOUSE_NUMBERS = ['3C', '3D', '3E', '3F', '3G', '3H', '3I']

ROOM_NUMBERS = ['11', '12', '13', '14', '21', '22', '31', '32', '41', '42', '43', '44', '111', '112', '113', '114',
                '121', '122', '123', '124', '131', '132', '133', '134', '141', '142', '143', '144', '211', '212', '213',
                '214', '221', '222', '223', '224', '231', '232', '233', '234', '241', '242', '243', '244']
