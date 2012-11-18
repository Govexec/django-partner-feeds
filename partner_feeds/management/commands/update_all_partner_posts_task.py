from django.core.management.base import BaseCommand, CommandError
from partner_feeds.ge_tasks import update_all_partner_posts_task

class Command(BaseCommand):
    help = 'Publish scheduled content.'

    def handle(self, *args, **options):
        try:

            update_all_partner_posts_task()

        except:
            raise CommandError("Failed to save static data feed.\n")

        self.stdout.write("Successfully saved static data feed.\n")
