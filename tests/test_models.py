import datetime

from django.test import TestCase

from django_proxy.models import Proxy

from tests.models import *


class BasicTests(TestCase):

    def test_models_with_status(self):
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)
        now = datetime.datetime.now()

        post = PostWithStatus()
        post.title = 'test title 1'
        post.slug = 'test-title-1'
        post.body = 'the body of my test'
        post.status = post.PUBLIC_STATUS
        post.tag_data = 'one two three'
        post.publish = now
        post.save()

        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        proxy = Proxy.objects.get(title='test title 1')
        self.assertEqual(proxy.title, 'test title 1')
        self.assertEqual(proxy.description, 'the body of my test')
        self.assertEqual(proxy.tags, 'one two three')
        self.assertEqual(proxy.pub_date, now)

        post.status = post.DRAFT_STATUS
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)

        post.status = post.PUBLIC_STATUS
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        PostWithStatus.objects.all().delete()


    def test_models_with_boolean(self):
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)
        now = datetime.datetime.now()

        post = PostBoolean()
        post.title = 'test title 2'
        post.slug = 'test-title-2'
        post.body = 'the body of my test'
        post.status = True
        post.tag_data = 'one two three'
        post.publish = now
        post.save()

        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        proxy = Proxy.objects.get(title='test title 2')
        self.assertEqual(proxy.title, 'test title 2')
        self.assertEqual(proxy.description, 'the body of my test')
        self.assertEqual(proxy.tags, 'one two three')
        self.assertEqual(proxy.pub_date, now)

        post.status = False
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)

        post.status = True
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        PostBoolean.objects.all().delete()


    def test_models_with_methods(self):
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)
        now = datetime.datetime.now()

        post = PostWithMethod()
        post.title = 'test title 3'
        post.slug = 'test-title-3'
        post.body = 'the body of my test'
        post.status = True
        post.tag_data = 'one two three'
        post.publish = now
        post.save()

        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        proxy = Proxy.objects.get(title='--test title 3--')
        self.assertEqual(proxy.title, '--test title 3--')
        self.assertEqual(proxy.description, '--the body of my test--')
        self.assertEqual(proxy.tags, '--one two three--')

        post.status = False
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 0)

        post.status = True
        post.save()
        proxy_count = Proxy.objects.count()
        self.assertEqual(proxy_count, 1)

        PostWithMethod.objects.all().delete()
