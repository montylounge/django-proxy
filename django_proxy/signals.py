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

        #does this piece of content care about active state awareness?
        if hasattr(cls,'active'):
            try:
                active_field = getattr(cls, 'active')
                objfield = active_field.keys()[0]
                active_status = active_field.values()[0]
                actual_status = getattr(instance, objfield, None)
                if not (active_status == actual_status):
                    return
            except Exception:
                #TODO: cleaner exception handling/messaging
                pass

        obj.content_object = instance
        obj.title = getattr(instance, cls.title, None)
        obj.description = getattr(instance, cls.description, None)

        #pub_date isn't required so confirm
        pub_date = getattr(cls, 'pub_date', None)
        if pub_date:
            obj.pub_date = getattr(instance, cls.pub_date)

        #tags aren't required so confirm
        tags = getattr(cls, 'tags', None)
        if tags:
            obj.tags = getattr(instance, cls.tags)
        obj.save()
    else:
        #this instance already exists let's try and grab it's Proxy instance
        try:
            ctype = ContentType.objects.get_for_model(instance)
            obj = model._default_manager.get(object_id=instance.id, content_type=ctype)
        except model.DoesNotExist:
            obj = model()
            obj.content_object = instance

        #does this piece of content care about active state awareness?
        active_field = getattr(cls, 'active')
        objfield = active_field.keys()[0]
        active_status = active_field.values()[0]
        actual_status = getattr(instance, objfield, None)

        if obj.id != None and hasattr(cls,'active'):
            try:
                if not (active_status == actual_status):
                    obj.delete()
                    return
            except Exception:
                #TODO: cleaner exception handling/messaging
                pass
        elif obj.id == None and hasattr(cls,'active'):
            #is this object in a state other than active if so return
            if not (active_status == actual_status):
                return


        obj.title = getattr(instance, cls.title, None)
        obj.description = getattr(instance, cls.description, None)

        #proxy pub_date isn't required so confirm
        pub_date = getattr(cls, 'pub_date', None)
        if pub_date:
            obj.pub_date = getattr(instance, cls.pub_date)

        #proxy tag isn't require so confirm
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
    try:
        obj =  model._default_manager.get(object_id=instance.id, content_type=ctype)
        obj.delete()
    except DoesNotExist:
        pass
