from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('zojax.django.socialauthentication.facebook.views',
    url(r'^login/$', 'facebook_login', name='facebook_login'),
    url(r'^done/$', 'facebook_done', name='facebook_done'),
)
