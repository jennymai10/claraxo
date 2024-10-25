from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, PermissionDenied


def delete_all_secrets(project_id):
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    try:
        # List all secrets in the project
        for secret in client.list_secrets(request={"parent": parent}):
            secret_name = secret.name
            try:
                # Delete the secret
                client.delete_secret(request={"name": secret_name})
                print(f"Deleted secret: {secret_name}")
            except NotFound:
                print(f"Secret not found: {secret_name}")
            except PermissionDenied:
                print(f"Permission denied: {secret_name}")
    except Exception as e:
        print(f"Error during deletion: {e}")

if __name__ == "__main__":
    # Replace with your Google Cloud project ID
    project_id = "c-lara"
    delete_all_secrets(project_id)