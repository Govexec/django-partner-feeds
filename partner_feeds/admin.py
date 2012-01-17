from django.contrib import admin
from partner_feeds.models import Partner, Post, PartnerGroup
from settings import STATIC_URL

class PartnerAdmin(admin.ModelAdmin):
	list_display = ['name', 'display_logo', 'feed_url', 'date_feed_updated',]

	def display_logo(self, instance):
		return '<img src="{0}{1}" />'.format(STATIC_URL, instance.logo )
	display_logo.allow_tags = True
	display_logo.short_description = 'Logo'

	fields = ['name', 'logo', 'url', 'feed_url']


class PostAdmin(admin.ModelAdmin):

	list_display = ['title', 'date', 'partner',]
	ordering = ['-date']
	list_filter = ('partner',)

class PartnerGroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'primary_category']

    filter_horizontal = ['partners',]

    prepopulated_fields = {"slug": ('title',)}

    
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PartnerGroup, PartnerGroupAdmin)