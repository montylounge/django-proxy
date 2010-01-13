from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django_proxy.managers import PublicManager

class ProxyBase(models.Model):
    '''Represents the proxy objects. Retains the name, description,
     and any tags related to the associated object.
     
    A good use, I've found, for this type of object is aggregate view of all
    content types in an RSS feed (post, links, tweets, etc.).
    
    '''
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    #denormalized fields
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    pub_date = models.DateTimeField(default=datetime.now)
    
    #audit fields
    created_on = models.DateTimeField(default=datetime.now)
    updated_on = models.DateTimeField(default=datetime.now)
    
    objects = PublicManager()
        
    def __unicode__(self):
        return '%s' % self.title
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        self.updated_on = datetime.now()
        super(ProxyBase, self).save(*args, **kwargs)


class Proxy(ProxyBase):
    '''The default proxy model.'''
    pass

