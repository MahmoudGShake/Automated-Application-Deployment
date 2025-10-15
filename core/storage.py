import base64
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
import os

class SignedMediaStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.salt = settings.MEDIA_SALT  # Salt value for encoding/decoding

    def encode_name(self, name):
        # Generate a hash of the file name with salt for unique encoding
        salted_name = f"{name}{self.salt}"
        # Encode the salted name in base64 URL-safe format
        b64_name = base64.urlsafe_b64encode(salted_name.encode()).decode()
        # Cache the original name for fast retrieval
        cache.set(f"media:{b64_name}", name, None)
        return b64_name

    def decode_name(self, b64_token):
        try:
            # Decode the base64 URL-safe encoded token
            salted_name = base64.urlsafe_b64decode(b64_token.encode()).decode()
            # Check if the decoded name contains the salt
            if self.salt not in salted_name:
                raise ValueError("Decoded token does not contain the expected salt")

            # Remove the salt to retrieve the original file name
            name = salted_name.replace(self.salt, "")
            # Validate that the file exists (this is optional but ensures the file is available)
            file_path = os.path.join(settings.MEDIA_ROOT, name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {name}")

            return name
        except (Exception, ValueError, FileNotFoundError) as e:
            # Handle any decoding, validation, or file-not-found errors
            return None

    def url(self, name):
        # Encode the name and return the URL with the base64 token
        b64_token = self.encode_name(name)
        return f"{settings.SIGNED_MEDIA_BASE_URL}/{b64_token}"  # URL with base64-encoded token