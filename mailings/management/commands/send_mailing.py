from django.core.management.base import BaseCommand, CommandError

from mailings.models import Mailing
from mailings.services import MailingNotAllowedError, send_mailing_now


class Command(BaseCommand):
    help = 'Запускает отправку рассылки по требованию (аналог кнопки "Отправить сейчас")'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки, которую нужно отправить')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с id={mailing_id} не найдена')

        try:
            result = send_mailing_now(mailing)
        except MailingNotAllowedError as exc:
            raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(
            f'Рассылка #{mailing.pk}: отправлено {result["sent"]} из {result["total"]}, '
            f'ошибок — {result["failed"]}.'
        ))
