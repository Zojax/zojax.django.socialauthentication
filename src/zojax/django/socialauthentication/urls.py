from django.conf.urls.defaults import patterns, url, include
from zojax.django.socialauthentication import settings


urlpatterns = patterns('',
    url(r'^login/$', 'django.views.generic.simple.direct_to_template', {'template': 'auth/login.html'}, name="auth_login"),                       
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="auth_logout"),                       
)

if settings.ENABLE_OPENID_AUTH:
    urlpatterns += patterns('',
        (r'^openid/', include('zojax.django.socialauthentication.openid.urls')),
    )

if settings.ENABLE_TWITTER_AUTH:
    urlpatterns += patterns('',
        (r'^twitter/', include('zojax.django.socialauthentication.twitter.urls')),
    )

if settings.ENABLE_FACEBOOK_AUTH:
    urlpatterns += patterns('',
        (r'^facebook/', include('zojax.django.socialauthentication.facebook.urls')),
    )
