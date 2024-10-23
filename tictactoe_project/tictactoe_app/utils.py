from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64, os
from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env.development') # MODIFY FOR PRODUCTION

# AES-CBC Decryption function with IV
def decrypt_data(encrypted_data, secret_key_64, iv_64):
    try:
        # Retrieve the secret key from backend environment variable
        secret_key_64 = os.getenv("SECRET_KEY")
        
        if not secret_key_64:
            raise ValueError("SECRET_KEY is not set in environment variables.")
        
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