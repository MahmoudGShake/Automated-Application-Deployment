from rest_framework.throttling import AnonRateThrottle,UserRateThrottle
from django.conf import settings
class CustomAnonRateThrottle(AnonRateThrottle):
	def __init__(self):
		super().__init__()
		self.duration = settings.REST_FRAMEWORK['BLOCK_PERIOD']
class CustomUserRateThrottle(UserRateThrottle):
	def __init__(self):
		super().__init__()
		self.duration = settings.REST_FRAMEWORK['BLOCK_PERIOD']


