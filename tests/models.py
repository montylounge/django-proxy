import datetime
import unittest

from django.core import signals
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from django_proxy.models import Proxy
from django_proxy.signals import proxy_save, proxy_delete


class BasePost(models.Model):
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish')
    body = models.TextField(_('body'))
    publish = models.DateTimeField(_('publish'))
    tag_data = models.CharField(_('tags'), max_length=200)

    class Meta:
        abstract = True
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title


class PostWithStatus(BasePost):
    """ PostWithStatus model """
    DRAFT_STATUS = 1
    PUBLIC_STATUS = 2
    STATUS_CHOICES = (
        (DRAFT_STATUS, _('Draft')),
        (PUBLIC_STATUS, _('Public')),
    )
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=PUBLIC_STATUS)

    class ProxyMeta:
        title = 'title'
        description = 'body'
        active = {'status': 2}
        pub_date = 'publish'
        tags = 'tag_data'


class PostBoolean(BasePost):
    """ PostBoolean model """
    status = models.BooleanField(default=True)

    class ProxyMeta:
        title = 'title'
        description = 'body'
        pub_date = 'publish'
        active = 'status'
        tags = 'tag_data'


class PostWithMethod(BasePost):
    """ PostWithMethod model """
    status = models.BooleanField(default=True)

    class ProxyMeta:
        title = 'get_title'
        description = 'get_description'
        #pub_date = 'get_publish'
        active = 'get_active'
        tags = 'get_tags'

    def get_active(self):
        return self.status

    def get_description(self):
        return '--%s--' % self.body

    def get_publish(self):
        return '--%s--' % self.publish

    def get_title(self):
        return '--%s--' % self.title

    def get_tags(self):
        return '--%s--' % self.tag_data


signals.post_save.connect(proxy_save, PostWithStatus, True)
signals.post_delete.connect(proxy_delete, PostWithStatus)

signals.post_save.connect(proxy_save, PostBoolean, True)
signals.post_delete.connect(proxy_delete, PostBoolean)

signals.post_save.connect(proxy_save, PostWithMethod, True)
signals.post_delete.connect(proxy_delete, PostWithMethod)
