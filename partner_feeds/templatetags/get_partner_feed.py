from coffin import template
from partner_feeds.models import Post

register = template.Library()

@register.object
def get_partner_feeds(partner_names=[], partner_ids=[], num=3):

	partners = []

	if len(partner_ids) > 0:

		for id in partner_ids:
			posts = list(Post.objects.filter(partner__id=id).select_related('partner').order_by("-date")[:num])
			if len(posts) > 0:
				partner = posts[0].partner
				partner.posts = posts
				partners.append(partner)

	elif len(partner_names) > 0:

		for name in partner_names:
			posts = list(Post.objects.filter(partner__name=name).select_related('partner').order_by("-date")[:num])
			if len(posts) > 0:
				partner = posts[0].partner
				partner.posts = posts
				partners.append(partner)

	return partners