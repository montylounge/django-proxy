from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType


def proxy_save(sender, **kwargs):
    ''' Handles the save/update of a Proxy instance. '''
    instance = kwargs['instance']
    created = kwargs['created']

    cls = instance.ProxyMeta
    model_str = getattr(cls, 'model_str', 'django_proxy.proxy')
    model = get_model(*model_str.split('.'))
    obj = model()
    active = False

    if created:
        obj.content_object = instance
    else:
        try:
            ctype = ContentType.objects.get_for_model(instance)
            obj = model._default_manager.get(object_id=instance.id, content_type=ctype)
        except model.DoesNotExist:
            obj = model()
            obj.content_object = instance

    if hasattr(cls, 'active'):
        if isinstance(cls.active, basestring):
            active_field = getattr(instance, cls.active, None)
            if callable(active_field):
                active = active_field()
            else:
                # test for Boolean field names, strings, etc
                pass
        else:
            try:
                active_field = cls.active
                objfield = active_field.keys()[0]
                active_status = active_field.values()[0]
                actual_status = getattr(instance, objfield, None)
                if active_status == actual_status:
                    active = True
            except Exception:
                # deal with this better...
                pass
    else:
        active = True

    if not active and obj.id:
        obj.delete()
        return

    if hasattr(cls, 'title'):
        title = getattr(instance, cls.title, None)
        if callable(title):
            obj.title = title()
        else:
            obj.title = title
    else:
        raise Exception('Missing title field')

    if hasattr(cls, 'description'):
        description = getattr(instance, cls.description, None)
        if callable(description):
            obj.description = description()
        else:
            obj.description = description
    else:
        raise Exception('Missing description field')

    #proxy pub_date isn't required so confirm
    if hasattr(cls, 'pub_date'):
        pub_date = getattr(instance, cls.pub_date, None)
        if callable(pub_date):
            obj.pub_date = pub_date()
        else:
            obj.pub_date = pub_date

    #proxy tag isn't require so confirm
    if hasattr(cls, 'tags'):
        tags = getattr(instance, cls.tags, None)
        if callable(tags):
            obj.tags = tags()
        else:
            obj.tags = tags

    if active:
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
        obj = model._default_manager.get(object_id=instance.id, content_type=ctype)
        obj.delete()
    except model.DoesNotExist:
        pass
