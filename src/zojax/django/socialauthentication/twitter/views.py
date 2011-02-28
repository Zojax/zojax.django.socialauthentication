from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from zojax.django.socialauthentication.twitter import oauthtwitter
from oauth.oauth import OAuthToken
from zojax.django.socialauthentication.settings import TWITTER_CONSUMER_KEY,\
    TWITTER_CONSUMER_SECRET
from django.conf import settings
import urlparse
 
 
def twitter_login(request):
    request.session['request_referer'] = urlparse.urljoin(request.META.get('HTTP_REFERER', ''), '/')
    twitter = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    request_token = twitter.getRequestToken()  
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.getSigninURL(request_token)  
    return HttpResponseRedirect(signin_url)
 
 
def twitter_done(request):
    request_token = request.session.get('request_token', None)
    verifier = request.GET.get('oauth_verifier', None)
    denied = request.GET.get('denied', None)
    # If we've been denied, put them back to the signin page
    # They probably meant to sign in with facebook >:D
    if denied:
        return HttpResponseRedirect(reverse("auth_login"))
 
    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
        # Redirect the user to the login page,
        return HttpResponseRedirect(reverse("auth_login"))
    
    token = OAuthToken.from_string(request_token)
    
    # If the token from session and token from twitter does not match
    #   means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['request_token']
        # Redirect the user to the login page
        return HttpResponseRedirect(reverse("auth_login"))
    
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, token)  
    access_token = twitter.getAccessToken()
    
    request.session['access_token'] = access_token.to_string()
    user = authenticate(request=request, twitter_access_token=access_token)
    
    # if user is authenticated then login user
    if user:
        login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponseRedirect(reverse('auth_login'))
 
    # authentication was successful, use is now logged in
    referer = request.session.get('request_referer')
    next_url = str(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
    if referer:
        next_url = urlparse.urljoin(referer, next_url)
        del request.session['request_referer']
    return HttpResponseRedirect(next_url)
        