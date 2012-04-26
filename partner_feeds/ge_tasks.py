

def update_all_partner_posts_task():
	"""
	Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
	"""
	import urllib
	from partner_feeds.models import Partner
	from datetime import datetime
	from content_utils.utils import expire_cache_by_path
	from partner_feeds.tasks import delete_old_posts
	from django.conf import settings

	number_of_new_posts = 0

	partners = Partner.objects.all()
	for partner in partners:
		# find all the posts in the current partner feeds and update them
		post_count = update_posts_for_feed_task(partner)
		number_of_new_posts = number_of_new_posts + post_count
		# Set the current time as when the partner feed was last retrieved
		Partner.objects.filter(pk=partner.pk).update(date_feed_updated=datetime.now())

	# clear home and early bird page cache and delete old posts if there is a change
	if number_of_new_posts > 0:
		expire_cache_by_path('/', is_view=False)
		expire_cache_by_path('/news/earlybird/', is_view=False)
		try:
			""" clear the NG Homepage cache by making a HTTP request to a view the clears the page cache by path """
			if not settings.DEBUG and settings.SITE_URL == 'http://www.govexec.com/':
				json_data = urllib.urlopen('http://apps1.ngprod.amc/clear_cache/?path=/').read()
		except :
			pass
		# set num_posts_to_keep to a high number to prevent clearing of active posts
		# that are then re-entered on next update
		delete_old_posts(num_posts_to_keep=200, celery=False)



def update_posts_for_feed_task(partner):
	"""
	Load and parse the RSS or ATOM feed associated with the given feed url, and for each entry, parse out the individual
	entries and save each one as a partner_feeds.
	"""
	from feedparser import parse
	from partner_feeds.models import Post
	from django.core.exceptions import ObjectDoesNotExist
	import timelib, re, time

	number_of_new_posts = 0
	feed = parse(partner.feed_url)

	for entry in feed.entries:
		p = Post()
		try:

			p.partner_id = partner.id
			p.title = entry.title

			p.subheader = entry.summary

			try:
				p.author = entry.author
			except AttributeError:
				pass

			try:
				p.guid = entry.id
			except AttributeError:
				p.guid = entry.link

			# try and select feed post to see if entry exists first
			try:
				Post.objects.get(guid=p.guid)
			except ObjectDoesNotExist:

				p.url = entry.link

				# try to get the date of the entry, otherwise, try the date of the feed
				try:
					entry_date = re.sub('\|','', entry.date)
					entry_date = timelib.strtotime(entry_date) # convert to a timestamp
					entry_date = time.localtime(entry_date) # converts to a time.struct_time (with regards to local timezone)
					entry_date = time.strftime("%Y-%m-%d %H:%M:%S", entry_date) # converts to mysql date format
					p.date = entry_date
				except AttributeError:
					p.date =  time.strftime("%Y-%m-%d %H:%M:%S",feed.date)

				p.save()
				number_of_new_posts = number_of_new_posts + 1
		except Exception:
			# TODO add sentry logging here
			# A catch all for errors so that the feed parsing does not break due to bad data
			pass
	# return number of added posts
	return number_of_new_posts




			

