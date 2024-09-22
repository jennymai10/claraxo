from google.cloud import secretmanager
from datetime import datetime

class Command(BaseCommand):
    help = "Clean up expired secrets in Google Cloud Secret Manager"

    def handle(self, *args, **kwargs):
        client = secretmanager.SecretManagerServiceClient()
        project_id = 'c-lara'
        secrets = client.list_secrets(request={"parent": f"projects/{project_id}"})
        
        for secret in secrets:
            # Check metadata or fetch secret version creation date and compare with current date
            # Here you would use the metadata you stored previously (like the TTL or expiration date)
            # Assume that we stored TTL in a database and fetched it here for simplicity
            secret_name = secret.name
            expiration_date = get_expiration_for_secret(secret_name)  # Custom function
            
            if expiration_date < datetime.utcnow():
                try:
                    client.delete_secret(request={"name": secret_name})
                    print(f"Deleted expired secret: {secret_name}")
                except Exception as e:
                    print(f"Failed to delete secret {secret_name}: {str(e)}")
