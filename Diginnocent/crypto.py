from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_signed_url(file_path,request):
    """
    Generate a signed URL for a given file path.

    Args:
        file_path (str): The relative path to the media file.
        expiration (int): Expiration time in seconds (default: 1 hour).

    Returns:
        str: The signed URL.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    signed_token = serializer.dumps(file_path)
    # Dynamically construct the base URL
    scheme = request.scheme  # 'http' or 'https'
    host = request.get_host()  # e.g., '127.0.0.1:8000'
    base_url = f"{scheme}://{host}"
    #return f"{base_url}/media/{signed_token}/?expires={expiration}"
    return f"{base_url}/media/{signed_token}/"
