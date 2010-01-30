import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model


class DjangoProxy(object):
    _required_fields = ['title', 'description']
    _field_mappings = [
        ('title', None),
        ('description', None),
        ('pub_date', datetime.datetime.now()),
        ('tags', None),
    ]
    content_object = None
    proxy_model = None

    def __init__(self, instance, created=None):
        self.content_object = instance
        model = self._get_proxy_model(instance)
        self.proxy_model = model()

        if created:
            self.proxy_model.content_object = instance
        else:
            try:
                ctype = ContentType.objects.get_for_model(instance)
                self.proxy_model = model._default_manager.get(object_id=instance.id, content_type=ctype)
            except model.DoesNotExist:
                self.proxy_model = model()
                self.proxy_model.content_object = instance

    def _get_attr(self, attr, obj):
        if hasattr(self.content_object.ProxyMeta, attr):
            value = getattr(self.content_object, getattr(obj, attr))
            if callable(value):
                value = value()
            return value

    def _get_proxy_model(self, instance):
        model_str = getattr(instance.ProxyMeta, 'model_str', 'django_proxy.proxy')
        model = get_model(*model_str.split('.'))
        return model

    def _validate(self):
        missing = []
        for field in self._required_fields:
            if not getattr(self.content_object.ProxyMeta, field, None):
                missing.append(field)
        if len(missing):
            raise ValueError('Missing required fields: %s' % (', '.join(missing)))

    def delete(self):
        """
        Remove any remaining child/associated Proxy records.

        """
        model = self._get_proxy_model(self.content_object)
        ctype = ContentType.objects.get_for_model(self.content_object)
        try:
            self.proxy_model = model._default_manager.get(object_id=self.content_object.id, content_type=ctype)
            self.proxy_model.delete()
        except model.DoesNotExist:
            pass

    def update(self):
        """
        Updates the status of the ProxyModel to either show or or get deleted
        depending on if the object is active.

        """
        self._validate()
        active = self.get_active()

        if active:
            for mapping in self._field_mappings:
                setattr(self.proxy_model, mapping[0], self._get_attr(mapping[0], self.content_object.ProxyMeta) or mapping[1])
            self.proxy_model.active = active
            self.proxy_model.save()
        elif self.proxy_model.id:
            self.proxy_model.delete()

    def get_active(self):
        active = False
        if hasattr(self.content_object.ProxyMeta, 'active'):
            if isinstance(self.content_object.ProxyMeta.active, basestring):
                active_field = getattr(self.content_object, self.content_object.ProxyMeta.active)
                if callable(active_field):
                    active_field = active_field()
                active = active_field

            elif isinstance(self.content_object.ProxyMeta.active, dict):
                try:
                    active_field = self.content_object.ProxyMeta.active
                    objfield = active_field.keys()[0]
                    active_status = active_field.values()[0]
                    actual_status = getattr(self.content_object, objfield)
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
    dp.update()


def proxy_delete(sender, **kwargs):
    """
    Responsible for handling the deletion of any child/associated Proxy records.

    Coupled to associated object's post_delete signal.

    """
    instance = kwargs['instance']

    dp = DjangoProxy(instance)
    dp.delete()
