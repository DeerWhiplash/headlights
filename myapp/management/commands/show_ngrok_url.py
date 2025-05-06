from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Prints the current Ngrok public URL'

    def handle(self, *args, **options):
        try:
            resp = requests.get('http://ngrok:4040/api/tunnels')
            tunnels = resp.json().get('tunnels')
            if tunnels:
                for tunnel in tunnels:
                    if tunnel['public_url'].startswith('https'):
                        self.stdout.write(self.style.SUCCESS(f"Ngrok public URL: {tunnel['public_url']}"))
                        return
                self.stdout.write(self.style.WARNING('No HTTPS tunnel found.'))
            else:
                self.stdout.write(self.style.WARNING('No tunnels found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching ngrok URL: {e}"))
