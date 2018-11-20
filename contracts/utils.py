from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# TODO: this is not local!


def render_html_to_pdf(source, context):
    template = get_template(source)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def save_html_as_pdf(source, destination, context):
    # open output file for writing (truncated binary)
    resultFile = open(destination, "w+b")

    template = get_template(source)
    html = template.render(context)

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            html,                # the HTML to convert
            dest=resultFile)           # file handle to recieve result

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err