# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import caching.base


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', models.ImageField(upload_to=b'img/upload/partner_logos', blank=True)),
                ('name', models.CharField(max_length=75)),
                ('url', models.URLField(help_text=b'Partner Website', verbose_name=b'URL')),
                ('feed_url', models.URLField(help_text=b'URL of a RSS or ATOM feed', unique=True, verbose_name=b'Feed URL')),
                ('date_feed_updated', models.DateTimeField(null=True, verbose_name=b'Feed last updated', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PartnerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(help_text=b'System uses this to lookup group, based on title', max_length=255)),
                ('meta_description', models.CharField(max_length=160)),
                ('meta_keywords', models.CharField(max_length=160)),
                ('partners', models.ManyToManyField(to='partner_feeds.Partner')),
                ('primary_category', models.ForeignKey(to='categories.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('subheader', models.TextField()),
                ('author', models.CharField(default=b'', max_length=255)),
                ('url', models.URLField()),
                ('guid', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('partner', models.ForeignKey(to='partner_feeds.Partner')),
            ],
            options={
                'ordering': ('-date',),
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
    ]
