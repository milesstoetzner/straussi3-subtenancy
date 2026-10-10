import os
from io import BytesIO
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.exceptions import SuspiciousFileOperation
from django.template.loader import get_template
from xhtml2pdf import pisa
from subtenancy.settings import BASE_DIR
import logging

logger = logging.getLogger(__name__)


def link_callback(uri, rel):
    """
    Resolves the /static/... URLs of the PDF templates to files on disk: the collected static files first
    (production, after collectstatic), the apps' static directories otherwise (development).

    Only URLs below STATIC_URL are resolved and only to files inside STATIC_ROOT or an app's static directory;
    anything else yields None, so xhtml2pdf cannot be pointed at arbitrary files.
    """
    if not uri.startswith(settings.STATIC_URL):
        return None
    path = uri[len(settings.STATIC_URL):]

    static_root = os.path.realpath(settings.STATIC_ROOT)
    collected = os.path.realpath(os.path.join(static_root, path))
    if collected.startswith(static_root + os.sep) and os.path.isfile(collected):
        return collected

    try:
        return finders.find(path)
    except SuspiciousFileOperation:
        # the finders refuse paths that would leave their directories
        logger.warning('refused suspicious static path in a PDF template: %r', uri)
        return None


def html_to_pdf(source, context):
    """
    Renders a PDF template (see pdf/page_templates.html for the page layout) to PDF bytes.
    """
    template = get_template(source)
    html = template.render({'signature_pages': (), **context})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, link_callback=link_callback, encoding='UTF-8')
    return result.getvalue()


def save_html_as_pdf(source, context, destination):
    pdf = html_to_pdf(source, context)
    file = open(destination, "w+b")
    file.write(pdf)
    file.close()

def contract_pdf_path(pk, version):
    filename = 'contract_' + str(pk) + '_version_' + str(version) + '.pdf'
    return os.path.join(BASE_DIR, 'contracts', 'contracts', os.path.basename(filename))

# page templates of contract.html that end with a signature line, see pdf/page_templates.html
SIGNATURE_PAGES = ('full', 'wore', 'melde', 'date', 'maintenant')

HOUSE_NUMBERS = ['3C', '3D', '3E', '3F', '3G', '3H', '3I']

ROOM_NUMBERS = ['11', '12', '13', '14', '21', '22', '31', '32', '41', '42', '43', '44', '111', '112', '113', '114',
                '121', '122', '123', '124', '131', '132', '133', '134', '141', '142', '143', '144', '211', '212', '213',
                '214', '221', '222', '223', '224', '231', '232', '233', '234', '241', '242', '243', '244']
