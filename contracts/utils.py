from django_tex.core import compile_template_to_pdf
from django.template.loader import get_template


def save_html_as_pdf(source, context, destination):
    pdf = html_to_pdf(source, context)
    file = open(destination, "w+b")
    file.write(pdf)
    file.close()


def html_to_pdf(source, context):
    template_name = 'contracts/contracts/' + source
    return compile_template_to_pdf(template_name, context)
