from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('zojax.django.socialauthentication.twitter.views',
    url(r'^login/$', 'twitter_login', name='twitter_login'),
    url(r'^done/$', 'twitter_done', name='twitter_done'),
)