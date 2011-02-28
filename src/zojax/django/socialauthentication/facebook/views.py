from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from zojax.django.socialauthentication.settings import FACEBOOK_API_KEY
import urllib
import simplejson
from django.conf import settings
import urlparse
 
 
def facebook_login(request):
    request.session['request_referer'] = urlparse.urljoin(request.META.get('HTTP_REFERER', ''), '/')
    params = {}
    params["api_key"] = FACEBOOK_API_KEY
    params["extern"] = "1"
    params["fbconnect"] = "1"
    params["fb_connect"] = "1"
    params["return_session"] = "1"
    params["v"] = "1.0"
#    params["next"] = request.build_absolute_uri(reverse("facebook_done")) # remove leading slash
    # Cancel link must be a full URL
    params["cancel"] = request.build_absolute_uri(reverse("auth_login"))
 
    url = "http://facebook.com/login.php?"+urllib.urlencode(params)
 
    return HttpResponseRedirect(url) 
 
 
def facebook_done(request):
    session = simplejson.loads(request.GET['session'])
    request.COOKIES[FACEBOOK_API_KEY + '_ss'] = session['secret']
    request.COOKIES[FACEBOOK_API_KEY + '_session_key'] = session['session_key']
    request.COOKIES[FACEBOOK_API_KEY + '_user'] = session['uid']
    request.COOKIES[FACEBOOK_API_KEY + '_expires'] = session['expires']
    request.COOKIES[FACEBOOK_API_KEY] = session['sig']
    user = authenticate(request = request)
    if user:
        login(request, user)
    else:
        return HttpResponse("FAILED")
        if FACEBOOK_API_KEY + '_session_key' in request.COOKIES:
            del request.COOKIES[FACEBOOK_API_KEY + '_session_key']
        if FACEBOOK_API_KEY + '_user' in request.COOKIES:    
            del request.COOKIES[FACEBOOK_API_KEY + '_user']
        return HttpResponseRedirect(reverse('auth_login'))
    
    referer = request.session.get('request_referer')
    next_url = str(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
    if referer:
        next_url = urlparse.urljoin(referer, next_url)
        del request.session['request_referer']
    return HttpResponseRedirect(next_url)
        