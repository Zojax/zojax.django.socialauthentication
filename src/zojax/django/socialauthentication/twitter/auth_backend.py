import urllib
import StringIO

from django.contrib.auth.models import User
from registration import signals
from zojax.django.socialauthentication import settings
from zojax.django.socialauthentication.models import AuthMeta, TwitterAccount
from zojax.django.socialauthentication.twitter import oauthtwitter
from django.core.files.uploadedfile import SimpleUploadedFile


class TwitterBackend:
    """TwitterBackend for authentication
    """
    def authenticate(self, request=None, twitter_access_token=None):
        '''authenticates the token by requesting user information from twitter
        '''
        if request is None:
            return None
        if not settings.ENABLE_TWITTER_REGISTRATION:
            return None
        if not twitter_access_token:
            return None
        twitter = oauthtwitter.OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, twitter_access_token)
        try:
            userinfo = twitter.GetUserInfo()
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise
        
        screen_name = userinfo.screen_name
        twitter_id = userinfo.id
        try:
            account = TwitterAccount.objects.get(twitter_id = twitter_id)
            user = account.user
            return user
        except TwitterAccount.DoesNotExist:
            #Create new user
            same_name_count = User.objects.filter(username__startswith = screen_name).count()
            if same_name_count:
                username = '%s%s' % (screen_name, same_name_count + 1)
            else:
                username = screen_name
            user = User(username =  username)
            name_data = userinfo.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except IndexError:
                first_name, last_name =  screen_name, ''
            user.first_name, user.last_name = first_name, last_name
            #user.email = '%s@example.twitter.com'%(userinfo.screen_name)
            user.save()
            account = TwitterAccount(user=user,
                              twitter_id=twitter_id,
                              screen_name=screen_name)
            # userprofile.access_token = access_token.key
            account.save()
            auth_meta = AuthMeta(user=user, provider='Twitter')
            auth_meta.portrait = userinfo.profile_image_url
            auth_meta.avatar = userinfo.profile_image_url
            auth_meta.location = userinfo.location
            auth_meta.save()
            signals.user_registered.send(sender=self.__class__,
                                         user=user,
                                         request=request)
            return user
 
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None