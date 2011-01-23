from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('zojax.django.socialauthentication.openid.views',
    url(r'^login/$', 'openid_login', name='openid_login'),
    url(r'^login/google/$', 'google_login', name='openid_login_google'),
    url(r'^login/yahoo/$', 'yahoo_login', name='openid_login_yahoo'),
    url(r'^complete/$', 'complete', name='openid_complete'),
    url(r'^done/$', 'done', name='openid_done'),
)