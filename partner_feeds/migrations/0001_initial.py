# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Partner'
        db.create_table('partner_feeds_partner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('feed_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('date_feed_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('partner_feeds', ['Partner'])

        # Adding model 'Post'
        db.create_table('partner_feeds_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('partner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['partner_feeds.Partner'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subheader', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('partner_feeds', ['Post'])

        # Adding model 'PartnerGroup'
        db.create_table('partner_feeds_partnergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('primary_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['categories.Category'])),
            ('meta_description', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('meta_keywords', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal('partner_feeds', ['PartnerGroup'])

        # Adding M2M table for field partners on 'PartnerGroup'
        db.create_table('partner_feeds_partnergroup_partners', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('partnergroup', models.ForeignKey(orm['partner_feeds.partnergroup'], null=False)),
            ('partner', models.ForeignKey(orm['partner_feeds.partner'], null=False))
        ))
        db.create_unique('partner_feeds_partnergroup_partners', ['partnergroup_id', 'partner_id'])


    def backwards(self, orm):
        
        # Deleting model 'Partner'
        db.delete_table('partner_feeds_partner')

        # Deleting model 'Post'
        db.delete_table('partner_feeds_post')

        # Deleting model 'PartnerGroup'
        db.delete_table('partner_feeds_partnergroup')

        # Removing M2M table for field partners on 'PartnerGroup'
        db.delete_table('partner_feeds_partnergroup_partners')


    models = {
        'categories.category': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alternate_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'alternate_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blog': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'meta_extra': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['categories.Category']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_converser_ad': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnail_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'partner_feeds.partner': {
            'Meta': {'object_name': 'Partner'},
            'date_feed_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'feed_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'partner_feeds.partnergroup': {
            'Meta': {'object_name': 'PartnerGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_description': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'partners': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['partner_feeds.Partner']", 'symmetrical': 'False'}),
            'primary_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['categories.Category']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'partner_feeds.post': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'Post'},
            'author': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['partner_feeds.Partner']"}),
            'subheader': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['partner_feeds']
