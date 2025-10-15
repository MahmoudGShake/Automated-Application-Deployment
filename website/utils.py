# utils.py
from django.urls import reverse

def get_site_url(request):
    """
    يرجّع رابط الموقع الرئيسي (بدون /admin).
    """
    # مثال: http://127.0.0.1:8000/ أو https://example.com/
    base_url = request.build_absolute_uri("/")
    return base_url.rstrip("/")
