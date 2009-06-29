from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

def proxy_save(sender, **kwargs):
    ''' Handles the save/update of a Proxy instance. '''
    instance = kwargs['instance']
    created = kwargs['created']
    
    cls = instance.ProxyMeta
    model_str = getattr(cls, 'model_str', 'django_proxy.proxy')
    model = get_model(*model_str.split('.'))

    #is this is a new instance?
    if created:
        obj = model()
        obj.content_object = instance
        obj.title = getattr(instance, cls.title, None)
        obj.description = getattr(instance, cls.description, None)
        obj.pub_date = getattr(instance, cls.pub_date, datetime.now())
        
        #tags aren't required so test
        tags = getattr(cls, 'tags', None)
        if tags:
            obj.tags = getattr(instance, cls.tags, None)
        obj.save()
    else:
        #this instance already exists let's try and grab it's Aggregate
        try:
            ctype = ContentType.objects.get_for_model(instance)
            obj = model._default_manager.get(object_id=instance.id, content_type=ctype)
        except model.DoesNotExist:
            obj = model()
            obj.content_object = instance

        obj.title = getattr(instance, cls.title, None)            
        obj.description = getattr(instance, cls.description, None)
        obj.pub_date = getattr(instance, cls.pub_date, datetime.now())
        
        #ag_tags must be string but default to None so we confirm
        tags = getattr(cls, 'tags', None)
        if tags:
            obj.tags = getattr(instance, cls.tags)
        obj.save()

def proxy_delete(sender, **kwargs):
    '''Responsible for handling the deletion of any child/associated Proxy records.
    
    Coupled to associated object's post_delete signal.
    
    '''
    instance = kwargs['instance']
    ctype = ContentType.objects.get_for_model(instance)

    cls = instance.ProxyMeta
    model_str = getattr(cls, 'model_str', 'django_proxy.proxy')
    model = get_model(*model_str.split('.'))    
    obj =  model._default_manager.get(object_id=instance.id, content_type=ctype)
    obj.delete()
