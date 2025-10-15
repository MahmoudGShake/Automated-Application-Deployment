from django.contrib import admin
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect,render
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (Category, Article, Section, Image, CustomUser,Link,HomeArticle,Team,TeamMember,
					 Footer,SubFooter,SubFooterCategory,NewsletterSubscription,Counter,Contact,
ContactRegistrationNumber,ContactAddress,ContactTelephone,Testimonial,Collaborator,FrequentlyAskedQuestion,
PulseHub,ContactFormSubmission,NewsLetter, NewsLetterArticle
					 )

from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect,HttpResponse
import nested_admin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.apps import apps
from django.utils.safestring import mark_safe
from website.signals import send_newsletter_message
admin.site.unregister(Group)
def add_field_to_fieldsets(fieldsets, changed_title,new_field,):
	updated_fieldsets = tuple(
		(title, {'fields': (new_field,*fields['fields'])}) if title == changed_title else (title, fields)
		for title, fields in fieldsets
	)

	return updated_fieldsets
def add_field_to_fileds_tuple(fieldsets, new_field):
	updated_fieldsets = tuple(
		# Check if the dictionary contains the 'fields' key
		(title, {
			**fields,
			'fields': (*fields['fields'], new_field)  # Add the new field dynamically
		}) if 'fields' in fields else (title, fields)
		for title, fields in fieldsets
	)
	return updated_fieldsets

# ----- Override AdminSite -----
class MyAdminSite(admin.AdminSite):

	def get_app_list(self, request, app_label=None):
		app_list = super().get_app_list(request, app_label)
		# ابحث عن app website و app auth
		website_app = next((a for a in app_list if a['app_label'] == 'website'), None)
		if not website_app:
			website_app = {
				'app_label': 'website',
				'app_url': '',
				'has_module_perms': True,
				'models': []
			}
			app_list.append(website_app)
		auth_app = next((a for a in app_list if a['app_label'] == 'auth'), None)
		if not auth_app:
			auth_app = {
				'app_label': 'auth',
				'app_url': '',
				'has_module_perms': True,
				'models': []
			}
			app_list.append(auth_app)
		if website_app:
			# ابحث عن موديل CustomUser داخل website
			user_model = next(
				(m for m in website_app['models'] if m['object_name'] == 'CustomUser'),
				None
			)
			if user_model:
				# احذفه من website
				website_app['models'].remove(user_model)

				# أضف user_model لقسم auth
				auth_app['models'].append(user_model)
				website_others_models = [m for m in website_app['models'] if
										 m['object_name'] in ["PulseHub", "Team", "TeamMember", "HomeArticle",
															  "Counter", "FrequentlyAskedQuestion", "Collaborator",
															  "Testimonial", "Contact", ]]
				for website_others_model in website_others_models:
					website_app['models'].remove(website_others_model)
				other_models_app = {
					'name': 'Other Models',
					'app_label': "other_models",
					'app_url': '',
					'has_module_perms': True ,
					'models': website_others_models
				}
				app_list.append(other_models_app)

		# تعريف الترتيب لكل app
		orderings = {
			"website": ["Category", "Article","ContactFormSubmission","NewsletterSubscription","NewsLetter","Footer"],
			"auth": ["CustomUser","Group"],
			"others": ["PulseHub","Team","TeamMember","HomeArticle","Counter","FrequentlyAskedQuestion","Collaborator","Testimonial","Contact"],
		}

		for app in app_list:
			if app["app_label"] in orderings:
				ordering = orderings[app["app_label"]]
				app["models"].sort(
					key=lambda x: ordering.index(x["object_name"])
					if x["object_name"] in ordering else len(ordering)
				)

		return app_list

# استبدل الـ admin الافتراضي بالـ custom
admin_site = MyAdminSite(name="myadmin")
@admin.register(CustomUser,site=admin_site)
class CustomUserAdmin(UserAdmin):
	UserAdmin.fieldsets = add_field_to_fieldsets(UserAdmin.fieldsets, 'Permissions', 'contact_form_submission_recipient')
	UserAdmin.add_fieldsets = add_field_to_fileds_tuple(UserAdmin.add_fieldsets, 'contact_form_submission_recipient')
	# Define the fields to display in list view
	list_display = UserAdmin.list_display + ('contact_form_submission_recipient',)
	# Customize the form for editing
	fieldsets = UserAdmin.fieldsets

	# Customize the form for adding a user
	add_fieldsets = UserAdmin.add_fieldsets + (
		(None, {'fields': ('contact_form_submission_recipient',)}),
	)


	# Make sure it is included in search if needed
	search_fields = UserAdmin.search_fields + ('contact_form_submission_recipient',)



class ImageInline(nested_admin.NestedStackedInline):
	model = Image
	extra = 0
	readonly_fields = ("image_url",)
class CategoryInline(nested_admin.NestedStackedInline):
	model = Category
	extra = 0

@admin.register(Category,site=admin_site)
class CategoryAdmin(nested_admin.NestedModelAdmin):
	#inlines = [ImageInline,CategoryInline,]
	inlines = [CategoryInline,]
	readonly_fields = ("url",)
	#list_display = ["id", "title", "description"]
	# Dynamically get all model fields
	def get_fieldsets(self, request, obj=None):
		# Check if obj is None (in case of adding a new object)
		if obj is None:
			# For new objects, simply use all the fields
			fields = [field.name for field in Category._meta.fields if not field.name == "id"]
		else:
			# If obj is not None, use the model instance's fields
			fields = [field.name for field in obj._meta.fields if not field.name == "id"]

		return (
			(None, {
				'fields': fields,  # List of field names
				'description': """
				here you can CRUD Category & its subcategories and you can use them in navbar and footer
				"""
			}),
		)

	list_display = ("id", "title","parent_category", "type","redirect_article")
	search_fields = ("title",)
	# يخلّي المقالات اللى تحت نفس الأب تيجي ورا بعض
	ordering = ("parent__title", "title")

	# فلترين: أب التصنيف ثم التصنيف نفسه (ويظهر بس اللى له مقالات)
	list_filter = (
		("parent", admin.RelatedOnlyFieldListFilter),
		("type", admin.ChoicesFieldListFilter),
	)

	@admin.display(ordering="parent__title", description="Parent Category")
	def parent_category(self, obj):
		return obj.parent or "there is no parent"


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		# لتقليل الاستعلامات فى الصفحة
		return qs.select_related("parent")
	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		type = obj.type
		base_url = reverse(type)
		if type == "news":
			obj.url = base_url + f"?id={obj.pk}&page=1#"
		else:
			obj.url = base_url + f"?id={obj.pk}#"
		obj.save(update_fields=["url"])

class LinkInline(nested_admin.NestedStackedInline):
	model = Link
	extra = 0

class SectionInline(nested_admin.NestedStackedInline):
	model = Section
	inlines = [LinkInline]
	extra = 0

def get_preview_name(obj):
	if obj.category and obj.category.type:
		if obj.category.type == "research":
			return "research"
		else:
			return f"{obj.category.type}_details"


@admin.register(Article,site=admin_site)
class ArticleAdmin(nested_admin.NestedModelAdmin):
	inlines = [ImageInline,SectionInline]
	#exclude = ("pin_date",)  # نخفيه من الفورم
	readonly_fields = ("created_by","created_at","preview_url","url","pin_date")
	def save_model(self, request, obj, form, change):
		if not change or not obj.created_by:  # لو إنشاء جديد أو created_by مش متحدد
			obj.created_by = request.user
		# for image_obj in obj.images.all():
		# 	if image_obj.image:
		# 		image_obj.image_url = request.build_absolute_uri(image_obj.image.url)
		# 		#image_obj.save(update_fields=["image_url"])
		# 	else:
		# 		image_obj.image_url = None
		# 		#image_obj.save(update_fields=["image_url"])#
		super().save_model(request, obj, form, change)



	def response_add(self, request, obj, post_url_continue=None):
		# بعد ما تعمل Save → يوجهك للـ preview

		preview_name = get_preview_name(obj)
		if preview_name:
			if obj.status == "draft":
				preview_url = reverse(preview_name) + f"?preview_id={obj.pk}"
				# return render(request, "redirect_preview.html", {"preview_url": preview_url})
				obj.preview_url = request.build_absolute_uri(preview_url)
			url = reverse(preview_name) + f"?id={obj.pk}"
			obj.url = request.build_absolute_uri(url)
			obj.save(update_fields=["url","preview_url"])
		# لو مش draft → يرجع السلوك الطبيعي
		for image_obj in obj.images.all():
			if image_obj.image:
				#image_obj.image_url = request.build_absolute_uri(image_obj.image.url)
				image_obj.image_url = request.scheme + "://" + request.get_host()
				image_obj.save(update_fields=["image_url"])
			else:
				image_obj.image_url = None
				image_obj.save(update_fields=["image_url"])#
		return super().response_add(request, obj, post_url_continue)

	def response_change(self, request, obj):
		preview_name = get_preview_name(obj)
		if preview_name:
			if obj.status == "draft":
				preview_url = reverse(preview_name) + f"?preview_id={obj.pk}"
				# return render(request, "redirect_preview.html", {"preview_url": preview_url})
				obj.preview_url = request.build_absolute_uri(preview_url)
			url = reverse(preview_name) + f"?id={obj.pk}"
			obj.url = request.build_absolute_uri(url)
			obj.save(update_fields=["url","preview_url"])
		for image_obj in obj.images.all():
			if image_obj.image:
				#image_obj.image_url = request.build_absolute_uri(image_obj.image.url)
				image_obj.image_url = request.scheme + "://" + request.get_host()
				image_obj.save(update_fields=["image_url"])
			else:
				image_obj.image_url = None
				image_obj.save(update_fields=["image_url"])
		return super().response_change(request, obj)
	def get_fieldsets(self, request, obj=None):
		# Check if obj is None (in case of adding a new object)
		if obj is None:
			# For new objects, simply use all the fields
			fields = [field.name for field in Article._meta.fields if not field.name == "id"]
		else:
			# If obj is not None, use the model instance's fields
			fields = [field.name for field in obj._meta.fields if not field.name == "id"]

		return (
			(None, {
				'fields': fields,  # List of field names
				'description': """
				here you can CRUD Article & its sections and you can use them in Categories(title and description in main page and sections in details)
				"""
			}),
		)
	#handeling preview
	list_display = ("id", "title","sub_category", "parent_category", "status","pin")
	search_fields = ("title",)
	# يخلّي المقالات اللى تحت نفس الأب تيجي ورا بعض
	ordering = ("category__parent__title", "category__title")

	# فلترين: أب التصنيف ثم التصنيف نفسه (ويظهر بس اللى له مقالات)
	list_filter = (
		("category__parent", admin.RelatedOnlyFieldListFilter),
		("category", admin.RelatedOnlyFieldListFilter),
	)
	@admin.display(ordering="category__parent__title", description="Parent Category")
	def parent_category(self, obj):
		return obj.category.parent or "there is no parent"

	@admin.display(ordering="category__title", description="Sub Category")
	def sub_category(self, obj):
		return obj.category
	def get_queryset(self, request):
		qs = super().get_queryset(request)
		# لتقليل الاستعلامات فى الصفحة
		return qs.select_related("category", "category__parent")



@admin.register(Group,site=admin_site)
class GroupAdmin(admin.ModelAdmin):
	pass

@admin.register(HomeArticle,site=admin_site)
class HomeArticleAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		model._meta.verbose_name = "Hero Section"
		model._meta.verbose_name_plural = "Hero Sections"

# ----- Team -----
class TeamMemebrInline(admin.StackedInline):
	model = TeamMember
	extra = 0
@admin.register(Team,site=admin_site)
class TeamAdmin(admin.ModelAdmin):
	inlines = [TeamMemebrInline]
@admin.register(TeamMember,site=admin_site)
class TeamMemberAdmin(admin.ModelAdmin):
	pass
# ----- End Team - Start Footer-----
class SubFooterCategoryInline(nested_admin.NestedStackedInline):
	model = SubFooterCategory
	extra = 0
class SubFooterInline(nested_admin.NestedStackedInline):
	model = SubFooter
	inlines = [SubFooterCategoryInline]
	extra = 0

@admin.register(Footer,site=admin_site)
class FooterAdmin(nested_admin.NestedModelAdmin):
	inlines = [SubFooterInline]
# ----- End Footer -----
@admin.register(NewsletterSubscription,site=admin_site)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
	list_display = ("id","name", "email", "news")
	readonly_fields = ("name","email","articles",)
	@admin.display(ordering="articles__title", description="News")
	def news(self, obj):
		return [article.id for article in obj.articles.all()] or "there is no News"

@admin.register(Counter,site=admin_site)
class CounterAdmin(admin.ModelAdmin):
	list_display = ("id", "satisfied_clients","successful_projects", "scientific_publications", "collaborating_countries")

#----- Start Contact -----
class ContactTelephoneInline(nested_admin.NestedStackedInline):
	model = ContactTelephone
	extra = 0
class ContactAddressInline(nested_admin.NestedStackedInline):
	model = ContactAddress
	extra = 0
class ContactRegistrationNumberInline(nested_admin.NestedStackedInline):
	model = ContactRegistrationNumber
	extra = 0
@admin.register(Contact,site=admin_site)
class ContactAdmin(nested_admin.NestedModelAdmin):
	inlines = [ContactTelephoneInline,ContactAddressInline,ContactRegistrationNumberInline]
@admin.register(Testimonial,site=admin_site)
class TestimonialAdmin(admin.ModelAdmin):
	pass
#----- Start Collaborators -----
@admin.register(Collaborator,site=admin_site)
class CollaboratorAdmin(admin.ModelAdmin):
	pass
@admin.register(FrequentlyAskedQuestion,site=admin_site)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
	pass
@admin.register(PulseHub,site=admin_site)
class PulseHubAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		model._meta.verbose_name = "PulseHub Platform Login Link"
		model._meta.verbose_name_plural = "PulseHub Platform Login Links"
@admin.register(ContactFormSubmission,site=admin_site)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
	can_delete = False
	readonly_fields = ("name","subject","email","message")
	list_display = ("id","name","subject","email")
class NewsLetterArticleInline(admin.StackedInline):
	model = NewsLetterArticle
	extra = 1   # عدد الصفوف الفارغة المبدئية
	autocomplete_fields = ['article']   # يسهل اختيار المقالات لو كثيرة
	fields = ['article',"custom_title","custom_description", 'clickers']    # الحقول التي ستظهر في الـ inline
	readonly_fields = ['clickers']
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		model._meta.verbose_name_plural = "News Letter Articles & Statistics"
@admin.register(NewsLetter,site=admin_site)
class NewsLetterAdmin(admin.ModelAdmin):
	pass
# 	inlines = [NewsLetterArticleInline]
# 	readonly_fields = ('newsletter_preview_section', 'newsletter_statistics_section')
#
# 	def get_fieldsets(self, request, obj=None):
# 		# نبدأ من fieldsets الأصلي (لو محدد في الأب)
# 		fieldsets = super().get_fieldsets(request, obj)
#
# 		# إذا كان العنصر موجود (أي صفحة التعديل وليس الإضافة)
# 		if obj:
# 			fieldsets += (
# 				('👁 Newsletter Preview', {
# 					'classes': ('tab',),
# 					'fields': ('newsletter_preview_section',),
# 				}),
# 				('📊 Newsletter Statistics', {
# 					'classes': ('tab',),
# 					'fields': ('newsletter_statistics_section',),
# 				}),
# 			)
#
# 		return fieldsets
#
# 	def newsletter_preview_section(self, obj):
# 		"""عرض محتوى النشرة البريدية داخل التبويب."""
# 		if not obj or not obj.pk:
# 			return "(Preview not available until the newsletter is saved.)"
#
# 		preview_html = send_newsletter_message(None, obj, preview=True)
# 		preview_full_html = f"""
# 		<div class="card mt-4">
#    <div class="card-header">
#         <h4>👁 Newsletter Preview</h4>
#     </div>
#     <div class="card-body" style="width: 100%; max-width: 1000px; margin: 0 auto;">
#         { preview_html }
#     </div>
#
#   </div>
# 		"""
# 		return mark_safe(preview_full_html)  # ✅ هذا هو المفتاح
#
# 	newsletter_preview_section.short_description = ""
# 	newsletter_preview_section.allow_tags = True
#
# 	def newsletter_statistics_section(self, obj):
# 		"""عرض الرسم البياني داخل التبويب."""
# 		if not obj or not obj.pk:
# 			return "(Statistics not available until the newsletter is saved.)"
#
# 		newsletter = obj
# 		articles = newsletter.articles.all()  # articles per newsletter
# 		labels = [f"{article.id} - {article.title}" for article in articles]
# 		values = []
# 		for article in articles:
# 			clickers = NewsLetterArticle.objects.get(
# 					newsletter_id=newsletter.id,
# 					article_id=article.id
# 				).clickers
# 			if clickers:
# 				values.append(clickers.all().count())
# 		print(labels)
# 		print(values)
# 		chart_html = f"""
# 	    <div class="card mt-4">
#     <div class="card-body" style="width: 100%; max-width: 1000px; margin: 0 auto;">
#       <canvas id="newsletterChart" style="height: 400px; width: 200%;"></canvas>
#     </div>
#
#   </div>
#   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
# <script>
#   document.addEventListener('DOMContentLoaded', () => {{
#     const ctx = document.getElementById('{{newsletterChart}}').getContext('2d');
#     const labels = { labels };
#     const values = { values};
#
#     // 🟦 إنشاء تدرج لوني ديناميكي يتغير حسب الوضع
#     const gradient = ctx.createLinearGradient(0, 0, 0, 400);
#     const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
#     if (isDarkMode) {{
#       gradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
#       gradient.addColorStop(1, 'rgba(54, 162, 235, 0.2)');
#     }} else {{
#       gradient.addColorStop(0, 'rgba(54, 162, 235, 0.6)');
#       gradient.addColorStop(1, 'rgba(54, 162, 235, 0.05)');
#     }}
#
#     new Chart(ctx, {{
#       type: 'bar',
#       data: {{
#         labels: labels,
#         datasets: [
#           {{
#             type: 'bar',
#             label: 'Clickers',
#             data: values,
#             backgroundColor: gradient,
#             borderRadius: 8,
#             barThickness: 'flex',
#             maxBarThickness: 40,
#           }},
#           {{
#             type: 'line',
#             label: 'Trend',
#             data: values,
#             borderColor: isDarkMode ? '#00e4ff' : '#007bff',
#             borderWidth: 2,
#             fill: false,
#             tension: 0.35,
#             pointRadius: 4,
#             pointHoverRadius: 6,
#             pointBackgroundColor: isDarkMode ? '#00e4ff' : '#007bff',
#           }}
#         ]
#       }},
#       options: {{
#         responsive: true,
#         maintainAspectRatio: false,
#         interaction: {{
#           mode: 'index',
#           intersect: false,
#         }},
#         animation: {{
#           duration: 1200,
#           easing: 'easeOutQuart'
#         }},
#         plugins: {{
#           legend: {{
#             labels: {{
#               color: isDarkMode ? '#ddd' : '#333',
#               font: {{ size: 13 }}
#             }}
#           }},
#           tooltip: {{
#             backgroundColor: isDarkMode ? '#222' : '#fff',
#             titleColor: isDarkMode ? '#fff' : '#000',
#             bodyColor: isDarkMode ? '#fff' : '#000',
#             borderColor: isDarkMode ? '#444' : '#ddd',
#             borderWidth: 1,
#             padding: 10,
#             displayColors: true,
#           }}
#         }},
#         scales: {{
#           x: {{
#             ticks: {{
#               color: isDarkMode ? '#ccc' : '#333',
#               font: {{ size: 12 }}
#             }},
#             grid: {{
#               display: false
#             }}
#           }},
#           y: {{
#             beginAtZero: true,
#             ticks: {{
#               stepSize: 1,
#               color: isDarkMode ? '#ccc' : '#333'
#             }},
#             grid: {{
#               color: isDarkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
#             }}
#           }}
#         }}
#       }}
#     }});
#   }});
# </script>
#
# 	    """
# 		return mark_safe(chart_html)  # ✅ مهم جدًا
#
# 	newsletter_statistics_section.short_description = ""
# 	newsletter_statistics_section.allow_tags = True
	pass
	inlines = [NewsLetterArticleInline]
	change_form_template = "admin/newsletter_change_form.html"

	def change_view(self, request, object_id, form_url='', extra_context=None):
		newsletter = self.get_object(request, object_id)
		extra_context = extra_context or {}

		articles = newsletter.articles.all() # articles per newsletter
		labels = [f"{article.id} - {article.title}" for article in articles]
		values = []
		for article in articles:
			clickers = NewsLetterArticle.objects.get(
					newsletter_id=newsletter.id,
					article_id=article.id
				).clickers
			if clickers:
				values.append(clickers.all().count())
		extra_context['chart_labels'] = labels
		extra_context['chart_values'] = values
		news_letter_preview = send_newsletter_message(None, newsletter,preview=True)
		extra_context['news_letter_preview'] = news_letter_preview
		return super().change_view(request, object_id, form_url, extra_context=extra_context)

