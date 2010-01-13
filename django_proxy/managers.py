from django.db.models import Manager
import datetime

class PublicManager(Manager):
    '''Retrieve all published objects.'''
    
    def published(self):
        return self.get_query_set().filter(pub_date__lte=datetime.datetime.now())