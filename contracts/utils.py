import os
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django_tex.core import compile_template_to_pdf


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


def test_html_to_pdf(source, context):
    template_name = 'contracts/contracts/str3.tex'
    PDF = compile_template_to_pdf(template_name, context)
    return PDF