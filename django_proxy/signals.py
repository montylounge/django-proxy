import datetime

from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType


class DjangoProxy(object):
    instance = None
    object = None
    proxy_model = None

    _required_fields = ['title', 'description']
    _field_mappings = [
        ('title', None),
        ('description', None),
        ('pub_date', datetime.datetime.now()),
        ('tags', None),
    ]

    def __init__(self, instance, created=None):
        self.instance = instance
        self.proxy_model = instance.ProxyMeta

        model = self._get_proxy_model(instance)
        self.object = model()

        if created:
            self.object.content_object = instance
        else:
            try:
                ctype = ContentType.objects.get_for_model(instance)
                self.object = model._default_manager.get(object_id=instance.id, content_type=ctype)
            except model.DoesNotExist:
                self.object = model()
                self.object.content_object = instance

    def _get_attr(self, attr, obj):
        if hasattr(self.proxy_model, attr):
            value = getattr(self.instance, getattr(obj, attr))
            if callable(value):
                return value()
            else:
                return value

    def _get_proxy_model(self, instance):
        model_str = getattr(instance.ProxyMeta, 'model_str', 'django_proxy.proxy')
        model = get_model(*model_str.split('.'))
        return model

    def _valdiate(self):
        missing = []
        for field in self._required_fields:
            if not getattr(self.proxy_model, field, None):
                missing.append(field)
        if len(missing):
            raise ValueError('Missing required fields: %s' % (', '.join(missing)))

    def create(self):
        self._valdiate()
        active = self.get_active()
        object = self.object

        if active:
            for mapping in self._field_mappings:
                setattr(object, mapping[0], self._get_attr(mapping[0], self.proxy_model) or mapping[1])
            object.active = active
            object.save()

        elif object.id:
            object.delete()

    def delete(self):
        """
        Remove any remaining child/associated Proxy records.

        """
        model = self._get_proxy_model(self.instance)
        ctype = ContentType.objects.get_for_model(self.instance)
        try:
            self.object = model._default_manager.get(object_id=self.instance.id, content_type=ctype)
            self.object.delete()
        except model.DoesNotExist:
            pass

    def get_active(self):
        active = False
        if hasattr(self.proxy_model, 'active'):
            if isinstance(self.proxy_model.active, basestring):
                active_field = getattr(self.instance, self.proxy_model.active)
                if callable(active_field):
                    active = active_field()
                else:
                    active = active_field

            elif isinstance(self.proxy_model.active, dict):
                try:
                    active_field = self.proxy_model.active
                    objfield = active_field.keys()[0]
                    active_status = active_field.values()[0]
                    actual_status = getattr(self.instance, objfield)
                    if active_status == actual_status:
                        active = True

                except Exception:
                    pass
        else:
            active = True

        return active


def proxy_save(sender, **kwargs):
    """
    Handles the save/update of a Proxy instance.

    """
    instance = kwargs['instance']
    created = kwargs['created']

    dp = DjangoProxy(instance, created)
    dp.create()


def proxy_delete(sender, **kwargs):
    """
    Responsible for handling the deletion of any child/associated Proxy records.

    Coupled to associated object's post_delete signal.

    """
    instance = kwargs['instance']

    dp = DjangoProxy(instance)
    dp.delete()
