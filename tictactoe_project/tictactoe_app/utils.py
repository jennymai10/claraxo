from google.cloud import secretmanager
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64, json
secret_key = 'YX9YLwraTdKLCvmLauhs100EGaSiTF+r0SdYz1jx1oY='

# class Command(BaseCommand):
#     help = "Clean up expired secrets in Google Cloud Secret Manager"

#     def handle(self, *args, **kwargs):
#         client = secretmanager.SecretManagerServiceClient()
#         project_id = 'c-lara'
#         secrets = client.list_secrets(request={"parent": f"projects/{project_id}"})
        
#         for secret in secrets:
#             # Check metadata or fetch secret version creation date and compare with current date
#             # Here you would use the metadata you stored previously (like the TTL or expiration date)
#             # Assume that we stored TTL in a database and fetched it here for simplicity
#             secret_name = secret.name
#             expiration_date = get_expiration_for_secret(secret_name)  # Custom function
            
#             if expiration_date < datetime.utcnow():
#                 try:
#                     client.delete_secret(request={"name": secret_name})
#                     print(f"Deleted expired secret: {secret_name}")
#                 except Exception as e:
#                     print(f"Failed to delete secret {secret_name}: {str(e)}")

# AES-CBC Decryption function with IV
def decrypt_data(encrypted_data, secret_key_64, iv_64):
    try:
        secret_key_64 = 'YX9YLwraTdKLCvmLauhs100EGaSiTF+r0SdYz1jx1oY='
        # Decode the base64-encoded secret key and IV
        secret_key = base64.b64decode(secret_key_64)
        iv = base64.b64decode(iv_64)

        # Decode the base64-encoded encrypted data
        encrypted_data_bytes = base64.b64decode(encrypted_data)

        # Create AES cipher object with the decoded secret key and IV
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)

        # Decrypt the data and unpad the plaintext
        decrypted_data = unpad(cipher.decrypt(encrypted_data_bytes), AES.block_size)

        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None