from datetime import datetime, timedelta

from coffin.shortcuts import render_to_response
from coffin.template import RequestContext
from coffin.template.response import TemplateResponse
from django.conf import settings
from django.views.generic import ListView

from partner_feeds.models import Post

class PostListView(ListView):
    response_class = TemplateResponse

    template_name = 'partner_feeds/select-feed.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        group = self.request.GET.get('partner-group', None)
        if group is None:
            return Post.objects.none()

        try:
            num_hours = int(self.request.GET.get('num-hours', 36))
        except:
            num_hours = 36

        min_datetime =  datetime.now() - timedelta(hours=num_hours)

        posts = (
            Post.objects
            .filter(
                partner__partnergroup__slug=group,
                date__gte=min_datetime
            )
            .order_by('-date')
            .select_related()
        )
        return posts

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context.update({
            'admin_title': settings.GRAPPELLI_ADMIN_TITLE,
            'app_label': Post._meta.app_label,
            'model_name': Post._meta.verbose_name_plural,
        })
        return context
