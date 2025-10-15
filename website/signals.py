from .models import NewsletterSubscription,Article,NewsLetter,NewsLetterArticle
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor
from django.forms.models import model_to_dict
from django.utils.timezone import now
from django.urls import reverse
from django.db import transaction


@receiver(pre_save, sender=Article)
def update_pin_date_on_pin(sender, instance, **kwargs):
	if not instance.pk:
		# مقال جديد
		if instance.pin and not instance.pin_date:
			instance.pin_date = now()
	else:
		old_pin = sender.objects.filter(pk=instance.pk).values_list('pin', flat=True).first()
		if old_pin is not None and old_pin is False and instance.pin is True:
			instance.pin_date = now()

def send_newsletter_message(newsletter_subscriber,news_letter,preview=False):
	try:
		message_content = ""
		for article in news_letter.articles.all():
			news_letter_article = NewsLetterArticle.objects.get(newsletter_id=news_letter.id,article_id=article.id)

			image_obj = article.images.all().first()
			if image_obj:
				news_image_url = image_obj.image_url + image_obj.image.url or ""
				image_alternative_text = image_obj.alternative_text
				news_image_tag = f"""<img src="{news_image_url}" alt="{image_alternative_text}" style="width: 100%; max-width: 550px; margin-top: 20px;">"""

			else:
				news_image_tag= ""
			article_url = article.url
			if article_url:
				if preview:
					article_url = f"{article_url}&subscriber_id=<subscriber_id>&newsletter_id={news_letter.id}"
				else:
					article_url = f"{article_url}&subscriber_id={newsletter_subscriber.id}&newsletter_id={news_letter.id}"

			article_custom_title = news_letter_article.custom_title
			if article_custom_title:
				article_title = article_custom_title
			else:
				article_title = article.title or ""
			article_custom_description = news_letter_article.custom_description
			if article_custom_description:
				article_description = article_custom_description
			else:
				article_description = article.description or ""
			div_tag = f"""
	                    <div class="content" style="padding: 20px;">
	                        
	                        <p class="news-title" style="font-size: 24px; font-weight: bold; color: #333;">{article_title}</p>
	                        <p class="news-meta" style="font-size: 14px; color: #777; margin-top: 10px;">
	                            <strong>By:</strong> {article.created_by.first_name + " " + article.created_by.last_name} | 
	                            <strong>Date:</strong> {article.created_at.strftime("%B %d, %Y")}
	                        </p>
	                        {news_image_tag}
	                        <p class="news-description" style="font-size: 16px; color: #555; margin-top: 10px;">{article_description}</p>
	                        <a href="{article_url or reverse('not_found')}" class="read-more-btn" style="display: inline-block; margin-top: 20px; background-color: #2C5234; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Read More</a>
	                    </div>
					"""
			message_content += div_tag
		if preview:
			subscriber_name = "Subscriber Name"
		else:
			subscriber_name = newsletter_subscriber.name
		after_dear_tag = news_letter.header_text or "Here Is The Latest News"
		subscriber_name_tag = f"<p>Dear {subscriber_name},</p><p>{after_dear_tag}</p>"
		kwarg = {"subscriber_name_tag":subscriber_name_tag,"news_letter_title":news_letter.title or "Newsletter","message_content":message_content}
		kwarg["footer_content"] = news_letter.footer_text or ""
		html_message = settings.NEWSLETTER_MESSAGE_TEMPLATE.format(**kwarg)
		if preview:
			return html_message
		msg = MIMEMultipart()
		msg['From'] = settings.DEFAULT_FROM_EMAIL
		msg['To'] = newsletter_subscriber.email  # Replace with the recipient's email address
		msg['Subject'] = settings.NEWSLETTER_MESSAGE_SUBJECT
		body = html_message
		msg.attach(MIMEText(body, 'html'))
		server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
		server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
		#print(msg.as_string())
		server.send_message(msg)
		server.quit()
	except Exception as e:
		pass
		#print(e)

def send_newsletter(instance):
	newsletter_subscribers = NewsletterSubscription.objects.all()
	with ThreadPoolExecutor() as executor:
		futures = [executor.submit(send_newsletter_message, newsletter_subscriber, instance,False) for newsletter_subscriber
		           in
		           newsletter_subscribers]

@receiver(pre_save, sender=NewsLetter)
def send_newsletter_to_subscribers(sender, instance, **kwargs):
	if not instance.pk:
		if instance.published:
			transaction.on_commit(lambda: send_newsletter(instance))
	else:
		old_published = sender.objects.filter(pk=instance.pk).values_list('published', flat=True).first()
		if old_published is not None and old_published is False and instance.published is True:
			send_newsletter(instance)