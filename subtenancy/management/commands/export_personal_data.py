import glob
import io
import json
import os
from datetime import date, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from pypdf import PdfReader, PdfWriter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from contracts.models import Contract
from contracts.utils import contract_pdf_path, html_to_pdf
from tenants.models import User


class Command(BaseCommand):
    help = ('Export all personal data stored about one person, for an access request under Art. 15 GDPR: as JSON '
            '(default, to stdout or --output) or as a PDF in the style of the contract documents (--pdf). '
            'Identify the person by username, e-mail address or id.')

    def add_arguments(self, parser):
        parser.add_argument('identifier', help='username, e-mail address or user id')
        parser.add_argument('--output', '-o', help='write the JSON to this file instead of stdout')
        parser.add_argument('--pdf', help='write a PDF report to this file')

    def handle(self, *args, **options):
        user = self.find_user(options['identifier'])
        report = self.build_report(user)

        if options['pdf']:
            with open(options['pdf'], 'wb') as f:
                f.write(self.build_pdf(report))
            self.stdout.write(self.style.SUCCESS(f'Exported data of {user} to {options["pdf"]}'))
            if not options['output']:
                return

        text = json.dumps(report, indent=2, ensure_ascii=False, default=self.encode)
        if options['output']:
            with open(options['output'], 'w', encoding='utf-8') as f:
                f.write(text + '\n')
            self.stdout.write(self.style.SUCCESS(f'Exported data of {user} to {options["output"]}'))
        else:
            self.stdout.write(text)

    @staticmethod
    def build_pdf(report):
        """
        One PDF: a table of contents, the report, then every version of every contract PDF the person is part of.
        The contents page is rendered last because it needs the page numbers, and re-rendered if it needs more
        than one page itself.
        """
        parts = [('Auskunft über gespeicherte personenbezogene Daten',
                  PdfReader(io.BytesIO(html_to_pdf('tenants/personal_data.html', dict(report, report=report)))))]
        for contract in report['contracts']:
            for filename in contract['pdf_files']:
                version = filename.rsplit('_', 1)[1].split('.')[0]
                parts.append((f'Vertrag {contract["id"]}, Version {version} ({filename})',
                              PdfReader(contract_pdf_path(contract['id'], version))))

        toc_pages = 1
        for _ in range(3):
            page, entries = toc_pages + 1, []
            for title, reader in parts:
                entries.append({'title': title, 'page': page})
                page += len(reader.pages)
            toc = PdfReader(io.BytesIO(html_to_pdf('tenants/personal_data_toc.html', {
                'account': report['account'], 'exported_at': report['exported_at'],
                'entries': entries, 'total_pages': page - 1})))
            if len(toc.pages) == toc_pages:
                break
            toc_pages = len(toc.pages)

        # xhtml2pdf writes its own outline from the headings; drop those and add one entry per part instead
        writer = PdfWriter()
        writer.append(toc, import_outline=False)
        writer.add_outline_item('Inhalt', 0)
        for (title, reader), entry in zip(parts, entries):
            writer.append(reader, import_outline=False)
            writer.add_outline_item(title, entry['page'] - 1)
        # continuous page numbers bottom left, matching the contents page (the contract documents keep their own
        # "Seite x von y" bottom right, which counts within the single document)
        total = len(writer.pages)
        for number, page in enumerate(writer.pages, start=1):
            page.merge_page(Command.page_number_overlay(number, total, float(page.mediabox.width), float(page.mediabox.height)))

        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()

    @staticmethod
    def page_number_overlay(number, total, width, height):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
        c.setFont('Helvetica', 9)
        c.drawString(25 * mm, 15 * mm, f'Auskunft Seite {number} von {total}')
        c.save()
        return PdfReader(buffer).pages[0]

    @staticmethod
    def find_user(identifier):
        query = Q(username=identifier) | Q(email__iexact=identifier)
        if identifier.isdigit():
            query |= Q(pk=int(identifier))
        users = list(User.objects.filter(query))
        if not users:
            raise CommandError(f'No user matches {identifier!r}')
        if len(users) > 1:
            raise CommandError(f'{identifier!r} matches several users: ' + ', '.join(str(u) for u in users))
        return users[0]

    @staticmethod
    def encode(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        raise TypeError(f'cannot serialize {type(value).__name__}')

    def build_report(self, user):
        report = {
            'exported_at': timezone.now(),
            'account': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'birthday': user.birthday,
                'phone_number': user.phone_number,
                'type': user.type,
                'type_display': str(user.get_type_display()),
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'groups': [g.name for g in user.groups.all()],
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'created_at': user.created_at,
                'updated_at': user.updated_at,
            },
        }

        contracts = Contract.objects.none()

        if user.is_maintenant():
            maintenant = user.maintenant
            report['maintenant'] = {
                'tenant_id': maintenant.tenant_id,
                'accepted_data_processing': maintenant.accepted_data_processing,
            }
            contracts = maintenant.contract_set.all()

        if user.is_subtenant():
            subtenant = user.subtenant
            report['subtenant'] = {
                'nationality': subtenant.nationality,
                'nationality_display': str(subtenant.get_nationality_display()),
                'correspondence_address': {
                    'name': subtenant.name,
                    'street': subtenant.street,
                    'house_number': subtenant.house_number,
                    'postcode': subtenant.postcode,
                    'city': subtenant.city,
                    'country': subtenant.country,
                    'country_display': str(subtenant.get_country_display()),
                },
                'accepted_data_processing': subtenant.accepted_data_processing,
            }
            request = subtenant.get_request()
            report['subtenancy_request'] = None if request is None else {
                'begin': request.begin,
                'end': request.end,
                'created_at': request.created_at,
                'updated_at': request.updated_at,
                'published_in_request_list': request.is_active(),
            }
            contracts = subtenant.contract_set.all()

        report['contracts'] = [self.contract_data(c, user) for c in contracts.order_by('pk')]

        report['not_included'] = [
            'Server access logs and the e-mails sent to you are kept outside this application (hosting and mail '
            'provider), see the privacy policy.',
            'Login, registration and password reset attempts are counted per IP address to limit abuse; only a hash '
            'of the address is kept in memory for at most one hour, the application stores no IP addresses.',
        ]
        return report

    @staticmethod
    def contract_data(contract, user):
        role = 'maintenant' if contract.maintenant_id == user.pk else 'subtenant'
        other = contract.subtenant if role == 'maintenant' else contract.maintenant
        pdfs = sorted(os.path.basename(p) for p in glob.glob(contract_pdf_path(contract.pk, '*')))
        return {
            'id': contract.pk,
            'your_role': role,
            'other_party': {'id': other.pk, 'name': other.get_full_name()},
            'begin': contract.begin,
            'end': contract.end,
            'house_number': contract.house_number,
            'room_number': contract.room_number,
            'rent': contract.rent,
            'caution': contract.caution,
            'caution_comment': contract.caution_comment,
            'condition': contract.condition,
            'condition_comment': contract.condition_comment,
            'donation': contract.donation,
            'is_maintenant_returning': contract.is_maintenant_returning,
            'is_maintenant_allowed': contract.is_maintenant_allowed,
            'is_maintenant_identified': contract.is_maintenant_identified,
            'is_subtenant_identified': contract.is_subtenant_identified,
            'is_subtenant_matriculated': contract.is_subtenant_matriculated,
            'is_subtenant_allowed_in_DE': contract.is_subtenant_allowed_in_DE,
            'has_special_permission': contract.has_special_permission,
            'is_active': contract.is_active,
            'version': contract.version,
            'pdf_files': pdfs,
            'created_at': contract.created_at,
            'updated_at': contract.updated_at,
        }
