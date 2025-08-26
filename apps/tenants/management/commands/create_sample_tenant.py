
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Create a sample tenant for development'
    
    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Tenant name', default='Sample Company')
        parser.add_argument('--domain', type=str, help='Tenant domain', default='localhost')
        parser.add_argument('--system', type=str, help='System parameter', 
                          default='You are a helpful customer service assistant. Be polite and professional.')
    
    def handle(self, *args, **options):
        tenant_name = options['name']
        tenant_domain = options['domain']
        system_param = options['system']
        
        tenant, created = Tenant.objects.get_or_create(
            domain=tenant_domain,
            defaults={
                'name': tenant_name,
                'system_parameter': system_param,
                'token_limit': 1000,
                'token_usage': 0
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created tenant: {tenant.name} ({tenant.domain})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Tenant already exists: {tenant.name} ({tenant.domain})')
            )
