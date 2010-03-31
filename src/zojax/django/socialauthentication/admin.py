from django.contrib import admin
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from models import TwitterAccount, FacebookAccount, OpenIdAccount, AuthMeta

admin.site.register([TwitterAccount, FacebookAccount, OpenIdAccount, AuthMeta])
