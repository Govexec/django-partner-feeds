import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from dateutil import tz
from feedparser import parse
from time import mktime, localtime, strftime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from content_utils.utils import expire_cache_by_path
from raven import Client

from newsletters.models import NewsletterPost # GE_NewsletterPost, NG_NewsletterPost
from partner_feeds.models import Partner, Post


logger = logging.getLogger(__name__)


def update_all_partner_posts_task():
    """
    Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
    """
    logger.debug("Running update_all_partner_posts_task.")

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
        logger.debug("Clearing site cache")
        expire_cache_by_path('/', is_view=False)
        expire_cache_by_path('/news/earlybird/', is_view=False)
        try:
            """ clear the NG Homepage cache by making a HTTP request to a view the clears the page cache by path """
            if not settings.DEBUG and settings.SITE_URL == 'http://www.govexec.com':
                clear_cache_cmd = os.path.join(settings.PROJECT_ROOT, 'support/clear_cache_for_external_sites.sh')
                # run the "clear_cache_for_external_sites.sh" to clear production NG and mobile site page caches
                subprocess.call([clear_cache_cmd, '2>&1', '>/dev/null', '&'])
        except:
            pass
        # set num_posts_to_keep to a high number to prevent clearing of active posts
        # that are then re-entered on next update
        delete_old_posts_tasks()
    logger.debug("Finished running update_all_partner_posts_task")


def utc_time_struct_to_local_time_struct(utc_time_struct):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    is_daylight_savings = localtime().tm_isdst
    local_time = datetime.fromtimestamp(mktime(utc_time_struct)).replace(tzinfo=from_zone).astimezone(to_zone)
    if is_daylight_savings:
        local_time = local_time - timedelta(hours=1)
    return local_time.timetuple()


def update_posts_for_feed_task(partner):
    """
    Load and parse the RSS or ATOM feed associated with the given feed url, and for each entry, parse out the individual
    entries and save each one as a partner_feeds.
    """
    logger.debug("Updating posts for partner feed: {} - {}.".format(partner, partner.pk))

    current_datetime = datetime.now()
    number_of_new_posts = 0
    feed = parse(partner.feed_url)

    for entry in feed.entries:
        p = Post()
        exception_data = {'entry': entry}
        try:

            p.partner_id = partner.id
            p.title = entry.title

            if not p.title or len(p.title) == 0:
                continue

            if hasattr(entry, 'summary'):
                p.subheader = entry.summary
            else:
                p.subheader = ''

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
                Post.objects.get(guid=p.guid, partner_id=partner.id)
                logger.debug("Prexisting partner_feed.Post with partner id: {}, guid: {}.".format(partner.id, p.guid))
                # print p.guid
                # print partner.id
                # TODO check to see if the story has been updated
            except ObjectDoesNotExist:
                logger.debug("partner_feed.Post does not exist with partner id: {}, guid: {}".format(partner.id, p.guid))
                # skip if URL is too long for database field
                max_length = 500
                if len(entry.link) > max_length:
                    logger.debug("Entry link is longer than {}. Skipping entry link {}.".format(max_length, entry.link))
                    continue

                p.url = entry.link

                # try to get the date of the entry, otherwise, use the current date
                if getattr(entry, 'published_parsed', None):
                    p.date = strftime("%Y-%m-%d %H:%M:%S", utc_time_struct_to_local_time_struct(entry.published_parsed))
                elif getattr(entry, 'updated_parsed', None):
                    p.date = strftime("%Y-%m-%d %H:%M:%S", utc_time_struct_to_local_time_struct(entry.updated_parsed))
                else:
                    p.date = current_datetime

                logger.debug("Saving partner_feed.Post with partner id: {}, guid: {}".format(partner.id, p.guid))
                p.save()
                logger.debug("Finished saving partner_feed.Post with partner id: {}, guid: {}".format(partner.id, p.guid))

                number_of_new_posts = number_of_new_posts + 1

        except Exception:
            client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
            client.captureException(exc_info=sys.exc_info(), data=exception_data)

    # return number of added posts
    return number_of_new_posts


def delete_old_posts_for_partner_task(partner):
    """
    Deletes all posts except for the most recent `num_posts_to_keep`
    Because Django won't let us do a delete of a query with an offset, we first find
    the IDs of the posts that we want to keep and then exclude them from the delete.
    """
    logger.debug("Finding posts to delete for partner {}".format(partner))

    # get active posts for partner to add to exclude list
    feed = parse(partner.feed_url)
    guids = set()
    for entry in feed.entries:
        try:
            guid = entry.id
        except AttributeError:
            guid = entry.link
        guids.add(guid)

    recent_posts = set(
        Post.objects
        .filter(partner_id=partner.id, guid__in=guids)
        .values_list("pk", flat=True)
    )

    # do not delete old posts if the active feed is empty or broken
    if not recent_posts:
        logger.debug("No posts to delete for partner {}".format(partner))
        return False

    # exclude posts with foreign key references in newsletter
    newsletter_posts = set(
        NewsletterPost.objects
        .exclude(ng_post=None)
        .values_list('ng_post_id', flat=True)
        .distinct()
    )
    recent_posts = recent_posts | newsletter_posts

    logger.debug("Deleting posts for partner {}, excluding {} posts".format(partner, len(recent_posts)))
    Post.objects.filter(partner=partner).exclude(pk__in=recent_posts).delete()


def delete_old_posts_tasks():
    """
    Fetch all partners, and for each partner,
    delete all but `num_posts_to_keep` number of posts
    """
    logger.debug("Deleting old posts")

    partners = Partner.objects.all()

    for partner in partners:
        delete_old_posts_for_partner_task(partner)
