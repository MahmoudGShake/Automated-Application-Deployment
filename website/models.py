from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser
import os,string,random
from core.storage import SignedMediaStorage
class CustomUser(AbstractUser):
	contact_form_submission_recipient = models.BooleanField(default=False,help_text="If checked, user will receive contact form submission emails")
	pass
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()
def category_types():
	navbar_path = os.path.join(settings.BASE_DIR, "templates", "navbar")
	files = os.listdir(navbar_path)
	category_mapping = {"research":"Research and Innovation",
						"products":"Products and Results",
						"teams":"DIC Team",
						"news":"DIC News",
						"qr_generator":"QR Code Generator",
						"dic-intro":"DIC Presentation",
						}
	choices = []
	for file_name in files:
		if file_name.endswith(".html"):
			file_name = file_name.replace(".html", "")
			display_file_name = category_mapping.get(file_name, file_name)
			choices.append((file_name, display_file_name))
	choices.append(("redirect_url", "Redirect URL"))
	choices.append(("redirect_article", "Redirect Article"))
	choices.append(("redirect_tag_id", "Redirect To Specific index Tag"))
	choices.append(("research", "About(same style like Research and Innovation)"))
	choices.append(("custom_html", "Custom HTML File"))
	return choices
tag_id_choices = (
	("hero","Hero tag(first tag in the index page)"),
	("footer","Footer tag(last tag in the index page)"),
	("contact","Contact Tag)"),
	("counts","Counts Tag)"),
	("news","News Tag)"),
	("clients","clients(Collaborators) Tag)"),
	("testimonials","Testimonials Tag)"),
)

class Category(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	redirect_url = models.URLField(blank=True, null=True)
	redirect_article = models.ForeignKey("website.Article",related_name="redirect_categories", on_delete=models.SET_NULL,null=True,blank=True)
	type = models.CharField(max_length=255,choices=category_types,null=True,blank=True)
	redirect_tag_id = models.CharField(max_length=255,choices=tag_id_choices,null=True,blank=True)
	custom_html_file = models.FileField(storage=SignedMediaStorage(),upload_to='templates/', blank=True, null=True)
	parent = models.ForeignKey(
		"self",
		related_name="subcategories",
		on_delete=models.CASCADE,
		blank=True,
		null=True
	)
	url = models.URLField(blank=True, null=True)
	class Meta:
		verbose_name = "Category"
		verbose_name_plural = "Categories"  # بدل Categorys
	def __str__(self):
		return f"{self.id} : {self.title}"

class Article(models.Model):
	STATUS_CHOICES = (
		("draft", "Draft"),
		("published", "Published"),
	)
	category = models.ForeignKey(Category,related_name="articles", on_delete=models.CASCADE)
	title = models.CharField(max_length=255, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	created_by = models.ForeignKey(User,related_name="articles", on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now=True)
	digital_twin_model = models.JSONField(null=True,blank=True,help_text="Tip : Must be list of 6 elements(faces)")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
	preview_url = models.URLField(blank=True, null=True)
	url = models.URLField(blank=True, null=True)
	pin = models.BooleanField(default=False)
	pin_date = models.DateTimeField(null=True,blank=True)
	def __str__(self):
		return f"{self.id} : {self.title}"
def replace_nth_occurrence(text, old, new, n):
	start = -1
	for i in range(n):
		start = text.find(old, start + 1)
		if start == -1:
			return text  # لو الـ old مش موجود كفاية مرات
	return text[:start] + new + text[start+len(old):]
class Section(models.Model):
	article = models.ForeignKey(Article,related_name="sections", on_delete=models.CASCADE)
	title = models.CharField(max_length=255, blank=True, null=True)
	content = models.TextField(blank=True, null=True)
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='section_images/', blank=True, null=True)

	@property
	def processed_content(self):
		if not self.content:
			return ""

		original_content = self.content
		links = self.links.all()
		for link in links:
			index = link.index
			if index == 0:
				original_content = original_content.replace(f"{link.text}", f'<a href="{link.link}">{link.text}</a>')
			else:
				original_content = replace_nth_occurrence(original_content, f"{link.text}",
														  f'<a href="{link.link}">{link.text}</a>', index)
		return original_content
	def __str__(self):
		return f"{self.id} : {self.article.title}({self.title})"
class Image(models.Model):
	article = models.ForeignKey(Article,related_name="images", on_delete=models.CASCADE,null=True,blank=True,help_text="Tip:Leave it blank if you create or update category")
	#category = models.ForeignKey(Category,related_name="category_images", on_delete=models.CASCADE,null=True,blank=True,help_text="Tip:Leave it blank if you create or update article")
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='article_images/', blank=True, null=True)
	alternative_text = models.TextField(blank=True, null=True)
	image_url = models.URLField(blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.article.title if self.article else self.category.title if self.category else ''}({self.image.name})"
class Link(models.Model):
	section = models.ForeignKey(Section, related_name="links", on_delete=models.CASCADE)
	text = models.CharField(max_length=255)
	link = models.CharField(max_length=255)
	index = models.IntegerField(default=0,help_text="Tip : index of link in section starts from 1 (0 to replace all text in section)")
	def __str__(self):
		return f"{self.id} : {self.section.title}({self.text},{self.index})"
class HomeArticle(models.Model):
	home_article_type_choices = (
		("hero", "Hero Article"),
		("about", "About Article"),
	)
	type = models.CharField(max_length=255, blank=True, null=True,choices=home_article_type_choices)
	h1_text = models.TextField(blank=True, null=True)
	h2_text = models.TextField(blank=True, null=True)
	p_text = models.TextField(blank=True, null=True)
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='home_images/', blank=True, null=True)
	image_alternative_text = models.TextField(blank=True, null=True)
	link = models.CharField(max_length=255,blank=True, null=True)
	link_text = models.CharField(max_length=255,blank=True, null=True)
	link_index = models.IntegerField(default=0,
								help_text="Tip : index of link in section starts from 1 (0 to replace all text in section)")
	button_text = models.CharField(max_length=255, blank=True, null=True)
	button_link = models.CharField(max_length=255, blank=True, null=True)
	@property
	def processed_p_text(self):
		if not self.p_text:
			return ""

		original_p_text = self.p_text
		link = self.link
		index = self.link_index
		link_text = self.link_text
		if index == 0:
			original_p_text = original_p_text.replace(f"{link_text}", f'<a href="{link}">{link_text}</a>')
		else:
			original_p_text = replace_nth_occurrence(original_p_text, f"{link_text}",
													  f'<a href="{link}">{link_text}</a>', index)
		return original_p_text

	def __str__(self):
		return f"{self.id} : {self.h1_text} : {self.type}"
class Team(models.Model):
	category = models.ForeignKey(Category, related_name="teams", on_delete=models.CASCADE)
	name = models.CharField(max_length=255, blank=True, null=True)
	title = models.CharField(max_length=255, blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.name}"
class TeamMember(models.Model):
	team = models.ForeignKey(Team,related_name="members", on_delete=models.CASCADE)
	name = models.CharField(max_length=255, blank=True, null=True)
	title = models.CharField(max_length=255, blank=True, null=True)
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='team_images/', blank=True, null=True)
	about = models.TextField(blank=True, null=True)
	linkedin = models.CharField(max_length=255, blank=True, null=True)
	website = models.CharField(max_length=255, blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.name}"
class Footer(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='footer_images/', blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	linkedin = models.URLField(blank=True, null=True)
	registered_addresses = models.TextField(blank=True, null=True)
	contact_addresses = models.TextField(blank=True, null=True)
	phone = models.CharField(max_length=255, blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.title}"
class SubFooter(models.Model):
	footer = models.ForeignKey(Footer,related_name="sub_footers", on_delete=models.CASCADE)
	title = models.CharField(max_length=255, blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.title}"
class SubFooterCategory(models.Model):
	sub_footer = models.ForeignKey(SubFooter,related_name="sub_footer_categories", on_delete=models.CASCADE)
	title = models.CharField(max_length=255, blank=True, null=True)
	category = models.ForeignKey(Category,related_name="categories", on_delete=models.CASCADE)
	def __str__(self):
		return f"{self.id} : {self.title}"
class NewsletterSubscription(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	created_at = models.DateTimeField(auto_now_add=True)
	articles = models.ManyToManyField(Article, related_name="newsletter_subscription_articles")
	def __str__(self):
		return f"{self.id} : {self.email}"
class NewsletterSubscriptionMessage(models.Model):
	code = models.CharField(max_length=255, blank=True, null=True)
	message = models.CharField(max_length=255, blank=True, null=True)
	color = models.CharField(max_length=255, blank=True, null=True)

	def generate_code(self):
		# Generate a random 6-character string with digits and lowercase letters
		characters = string.ascii_lowercase + string.digits
		return ''.join(random.choice(characters) for _ in range(6))

	def save(self, *args, **kwargs):
		if not self.code:
			self.code = self.generate_code()  # Generate code if not already set
		super(NewsletterSubscriptionMessage, self).save(*args, **kwargs)

class Counter(models.Model):
	satisfied_clients = models.IntegerField(blank=True, null=True)
	successful_projects = models.IntegerField(blank=True, null=True)
	scientific_publications = models.IntegerField(blank=True, null=True)
	collaborating_countries = models.IntegerField(blank=True, null=True)
	def __str__(self):
		return f"{self.id}"
class Contact(models.Model):
	email = models.EmailField(blank=True, null=True)
	linkedin = models.CharField(max_length=255,blank=True, null=True)
	location = models.CharField(max_length=255,blank=True, null=True)
	def __str__(self):
		return f"{self.id}"
class ContactTelephone(models.Model):
	contact = models.ForeignKey(Contact,related_name="telephones", on_delete=models.CASCADE)
	telephone = models.CharField(max_length=255,blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.telephone}"
class ContactAddress(models.Model):
	contact = models.ForeignKey(Contact,related_name="addresses", on_delete=models.CASCADE)
	country = models.CharField(max_length=255,blank=True, null=True)
	registered_address = models.CharField(max_length=255,blank=True, null=True)
	contact_address = models.CharField(max_length=255,blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.country}"
class ContactRegistrationNumber(models.Model):
	contact = models.ForeignKey(Contact,related_name="registration_numbers", on_delete=models.CASCADE)
	country = models.CharField(max_length=255,blank=True, null=True)
	registration_title1 = models.CharField(max_length=255,blank=True, null=True)
	registration_number1 = models.CharField(max_length=255,blank=True, null=True)
	registration_title2 = models.CharField(max_length=255, blank=True, null=True)
	registration_number2 = models.CharField(max_length=255, blank=True, null=True)
	registration_title3 = models.CharField(max_length=255, blank=True, null=True)
	registration_number3 = models.CharField(max_length=255, blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.country}"
class Testimonial(models.Model):
	name = models.CharField(max_length=255, blank=True, null=True)
	title = models.CharField(max_length=255, blank=True, null=True)
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='testimonial_images/', blank=True, null=True)
	feedback = models.TextField(blank=True, null=True)
	stars = models.IntegerField(blank=True, null=True)
	def __str__(self):
		return f"{self.id} : {self.name}"
class Collaborator(models.Model):
	image = models.ImageField(storage=SignedMediaStorage(),upload_to='collaborator_images/')
	def __str__(self):
		return f"{self.id} : {self.image.name}"
class FrequentlyAskedQuestion(models.Model):
	faq_types = [
		('faqlist1', 'FAQ List 1'),
		('faqlist2', 'FAQ List 2'),
	]
	question = models.CharField(max_length=255)
	answer = models.TextField()
	type = models.CharField(max_length=255,choices=faq_types)
	def __str__(self):
		return f"{self.id} : {self.question}"
class PulseHub(models.Model):
	link = models.CharField(max_length=255)
	def __str__(self):
		return f"{self.id} : {self.link}"
class ContactFormSubmission(models.Model):
	name = models.CharField(max_length=255)
	subject = models.CharField(max_length=255)
	email = models.EmailField()
	message = models.TextField()
	def __str__(self):
		return f"{self.id} : {self.name}"


class NewsLetter(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	header_text = models.TextField(blank=True, null=True)
	footer_text = models.TextField(blank=True, null=True)
	articles = models.ManyToManyField(Article,related_name="newsletter_articles",through='NewsLetterArticle',)
	published = models.BooleanField(default=False)
	def __str__(self):
		return f"{self.id} : {self.title}"
class NewsLetterArticle(models.Model):
	newsletter = models.ForeignKey(NewsLetter, on_delete=models.CASCADE)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	custom_title = models.CharField(max_length=255, blank=True, null=True)
	custom_description = models.TextField(blank=True, null=True)
	clickers = models.ManyToManyField(NewsletterSubscription, blank=True)

	#custom_image = models.ImageField(storage=SignedMediaStorage(),upload_to='newsletter_images/', blank=True, null=True)

	class Meta:
		unique_together = ('newsletter', 'article')

	def __str__(self):
		return f"{self.newsletter.title} - {self.article.title}"