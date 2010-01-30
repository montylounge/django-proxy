import datetime
import unittest

from django.core import signals
from django.db import models
from django.db.models import signals
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from django_proxy.models import Proxy
from django_proxy.signals import proxy_save, proxy_delete

from tests.models import *
from tests.test_models import *
