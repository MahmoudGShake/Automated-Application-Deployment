from rest_framework import serializers
from .models import Article,Section,Image,Category
from Diginnocent.crypto import generate_signed_url
from django.conf import settings
from typing import Optional, Dict, Any,AnyStr,List
def secure_url(self,file):
	request = self.context.get('request')
	return generate_signed_url(file.name, request)
def get_media_url(request, path):
	# Dynamically build the media URL based on the request's protocol
	protocol = request.scheme  # 'http' or 'https'
	#return f"{protocol}://{request.get_host()}{settings.MEDIA_URL}{path}"
	if settings.MEDIA_HTTPS:
		protocol = 'https'
	else:
		protocol = 'http'
	#return f"{protocol}://{request.get_host()}{path}"
	return generate_signed_url(path,request)

def get_ftp_file_url(self, obj, file_type):
	file_obj = getattr(obj, file_type, None)
	if not file_obj:
		return None

	request = self.context.get('request')
	try:
		if file_obj:
			# Return the full URL using request.build_absolute_uri
			#return request.build_absolute_uri(file_obj.url) if request else file_obj.url

			return get_media_url(request,file_obj.name)
	except Exception as e:
		try:
			return f"error: {e}"
			#return file_obj.url
		except:
			return None


	return None
def get_image_url(self, obj) -> Any:
	return get_ftp_file_url(self, obj,"image")
def replace_nth_occurrence(text, old, new, n):
	start = -1
	for i in range(n):
		start = text.find(old, start + 1)
		if start == -1:
			return text  # لو الـ old مش موجود كفاية مرات
	return text[:start] + new + text[start+len(old):]
class SectionSerializer(serializers.ModelSerializer):
	image_url = serializers.SerializerMethodField()
	content = serializers.SerializerMethodField()
	class Meta:
		model = Section
		fields = ["id","title","content","image","image_url"]
		extra_kwargs = {'image': {'write_only': True}}
	def get_content(self, obj) -> AnyStr:
		original_content = obj.content
		if not original_content:
			return original_content
		else:
			links = obj.links.all()
			for link in links:
				index = link.index
				if index == 0:
					original_content = original_content.replace(f"{link.text}", f'<a href="{link.link}">{link.text}</a>')
				else:
					original_content = replace_nth_occurrence(original_content,f"{link.text}", f'<a href="{link.link}">{link.text}</a>',index)
			return original_content
	def get_image_url(self, obj) -> AnyStr:
		return get_image_url(self, obj)
class ImageSerializer(serializers.ModelSerializer):
	image_url = serializers.SerializerMethodField()
	class Meta:
		model = Image
		fields = ["id","image","image_url"]
		extra_kwargs = {'image': {'write_only': True}}
	def get_image_url(self, obj) -> AnyStr:
		return get_image_url(self, obj)
class ArticleSerializer(serializers.ModelSerializer):
	sections = SectionSerializer(many=True)
	images = ImageSerializer(many=True)

	class Meta:
		model = Article
		fields = ["id", "title", "description", "sections", "images"]

	def __init__(self, *args, **kwargs):
		without_details = kwargs.pop('without_details', False)
		super().__init__(*args, **kwargs)

		if without_details:
			for field in ["description", "images"]:
				self.fields.pop(field, None)  # None to avoid KeyError
class CategorySerializer(serializers.ModelSerializer):
	subcategories = serializers.SerializerMethodField()

	class Meta:
		model = Category
		fields = ["id", "title", "description", "subcategories"]

	def __init__(self, *args, **kwargs):
		without_details = kwargs.pop('without_details', False)
		super().__init__(*args, **kwargs)

		if without_details:
			for field in ["description", "subcategories"]:
				self.fields.pop(field, None)  # None to avoid KeyError

	def get_subcategories(self, obj):
		# عشان يكون عندك recursion لازم تستدعي نفس الـ serializer
		queryset = obj.subcategories.all()
		serializer = CategorySerializer(
			queryset,
			many=True,
			context=self.context
		)
		return serializer.data


