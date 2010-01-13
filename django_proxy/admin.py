from django.contrib import admin
from django.contrib.contenttypes import generic
from django_proxy.models import Proxy

class ProxyAdmin(admin.ModelAdmin):
    '''Represents proxy model in the admin. 
    
    #TODO: would like to limit content type filter to only those
    content types that exist for the proxy and not ALL content_types.
    '''
    search_fields = ('title',)
    list_filter = ('content_type',)
    list_display     = ('title', 'object_id', 'description', 'tags', 'content_type',)

admin.site.register(Proxy, ProxyAdmin)
