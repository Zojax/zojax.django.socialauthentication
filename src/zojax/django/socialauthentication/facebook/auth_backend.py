from django.contrib.auth.models import User
from registration import signals
from zojax.django.socialauthentication.facebook.facebook import \
    getFacebookUserId, getFacebookUserInfo
from zojax.django.socialauthentication.models import AuthMeta, FacebookAccount
from zojax.django.socialauthentication.settings import ENABLE_FACEBOOK_REGISTRATION
import random


class FacebookBackend:
    
    def authenticate(self, request = None):
        if not request:
            return None
        
        if not ENABLE_FACEBOOK_REGISTRATION:
            return None
        fb_user = getFacebookUserId(request)
        
        if not fb_user:
            return None
        
 
        try:
            account = FacebookAccount.objects.get(facebook_id = str(fb_user))
            return account.user
        except FacebookAccount.DoesNotExist:
            fb_data = getFacebookUserInfo(fb_user)
                
            if not fb_data:
                return None
 
            username = fb_data.get('username')
            generate_username = False
            
            if username is None:
                generate_username = True
                username =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])

            cnt = 1
            base_username = username
            while User.objects.filter(username = username).count():
                username = "%s-%i" % (base_username, cnt)
                cnt += 1
                
            user = User.objects.create(username = username)
            user.first_name = fb_data['first_name']
            user.last_name = fb_data['last_name']
            user.save()
            account = FacebookAccount(facebook_id = str(fb_data['uid']), user = user)
            account.save()
            
            if generate_username:
                username = "facebookuser-%i" % account.id
                while User.objects.filter(username = username).count():
                    username += random.choice('abcdefghijklmnopqrstuvwxyz')
                user.username = username
                user.save()
            
            auth_meta = AuthMeta(user=user, provider='Facebook')
            auth_meta.save()
            
            signals.user_registered.send(sender=self.__class__,
                                         user=user,
                                         request=request)
            return user
        
        return None
 
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None