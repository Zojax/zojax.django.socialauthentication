from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from zojax.django.socialauthentication import settings
from zojax.django.socialauthentication.twitter import oauthtwitter
from oauth.oauth import OAuthToken
 
 
def twitter_login(request):
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
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
        return HttpResponseRedirect(reverse("socialauth_login_page"))
    
    twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, token)  
    access_token = twitter.getAccessToken()
    
    request.session['access_token'] = access_token.to_string()
    user = authenticate(twitter_access_token=access_token)
    
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
    return HttpResponseRedirect(getattr(settings, "LOGIN_NEXT_URL", "/"))
        