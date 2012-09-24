import sys
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from sentry.client.models import client as sentry_client

def update_all_partner_posts_task():
    """
    Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
    """
    from partner_feeds.models import Partner
    from datetime import datetime
    from content_utils.utils import expire_cache_by_path

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
                clear_cache_cmd = os.path.join(settings.PROJECT_ROOT, 'support/clear_cache_for_external_sites.sh')
                # run the "clear_cache_for_external_sites.sh" to clear production NG and mobile site page caches
                import subprocess
                subprocess.call([clear_cache_cmd, '2>&1', '>/dev/null', '&'])
        except :
            pass
        # set num_posts_to_keep to a high number to prevent clearing of active posts
        # that are then re-entered on next update
        delete_old_posts_tasks()



def update_posts_for_feed_task(partner):
    """
    Load and parse the RSS or ATOM feed associated with the given feed url, and for each entry, parse out the individual
    entries and save each one as a partner_feeds.
    """
    from feedparser import parse
    from partner_feeds.models import Post
    import timelib, re, time
    from datetime import datetime

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
                Post.objects.get(guid=p.guid)
                # TODO check to see if the story has been updated
            except ObjectDoesNotExist:

                current_datetime = datetime.now()

                p.url = entry.link

                # try to get the date of the entry, otherwise, try the date of the feed
                try:
                    entry_date = re.sub('\|','', entry.date)
                    entry_date = timelib.strtotime(entry_date) # convert to a timestamp
                    entry_date = time.localtime(entry_date) # converts to a time.struct_time (with regards to local timezone)
                    entry_date = time.strftime("%Y-%m-%d %H:%M:%S", entry_date) # converts to mysql date format
                    p.date = entry_date
                except AttributeError:
                    if hasattr(feed, 'date') and feed.date:
                        if type(feed.date).__name__ == 'str':
                            # Fri, 11 May 2012 05:14:37 GMT
                            try:
                                feed.date = datetime.strptime(feed.date, '%a, %d %b %Y %H:%M:%S %Z')
                            except ValueError:
                                # Fri, 27 Apr 2012 22
                                feed.date = datetime.strptime(feed.date, '%a, %d %b %Y %H')
                            # pass
                        p.date = feed.date

                if not p.date or (type(p.date).__name__ == 'datetime' and p.date > current_datetime):
                    if settings.DEBUG:
                        try:
                            print 'entry_date: %s' % entry_date
                            print 'entry.date: %s' % entry.date
                            print 'feed.date: %s' % feed.date
                        except Exception, exc:
                            pass
                    p.date = current_datetime

                p.save()

                number_of_new_posts = number_of_new_posts + 1

        except Exception, exc:
            sentry_client.create_from_exception(exc_info=sys.exc_info(), data=exception_data)
            continue

    # return number of added posts
    return number_of_new_posts

def delete_old_posts_for_partner_task(partner):
    """
    Deletes all posts except for the most recent `num_posts_to_keep`
    Because Django won't let us do a delete of a query with an offset, we first find
    the IDs of the posts that we want to keep and then exclude them from the delete.
    """
    from partner_feeds.models import Post
    from newsletters.models import NewsletterPost # GE_NewsletterPost, NG_NewsletterPost
    from feedparser import parse

    # get active posts for partner to add to exclude list
    recent_posts = []
    feed = parse(partner.feed_url)
    for entry in feed.entries:
        try:
            guid = entry.id
        except AttributeError:
            guid = entry.link

        try:
            post = Post.objects.get(guid=guid)
            recent_posts.append(post.id)
        except ObjectDoesNotExist:
            pass

    # do not delete old posts if the active feed is empty or broken
    if len(recent_posts) == 0:
        return False

    # recent_posts = list(Post.objects.filter(partner=partner).values_list('id', flat=True)[:num_posts_to_keep])

    # exclude posts with foreign key references in newsletter
    newsletter_posts = list(NewsletterPost.objects.exclude(post=None).values_list('post_id', flat=True))
    if len(newsletter_posts) > 0:
        recent_posts = recent_posts + newsletter_posts

    Post.objects.filter(partner=partner).exclude(pk__in=list(set(recent_posts))).delete()


def delete_old_posts_tasks():
    """
    Fetch all partners, and for each partner,
    delete all but `num_posts_to_keep` number of posts
    """
    from partner_feeds.models import Partner

    partners = Partner.objects.all()

    for partner in partners:
        delete_old_posts_for_partner_task(partner)
