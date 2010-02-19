from django.contrib.auth.models import User
from registration import signals
from zojax.django.socialauthentication import settings
from zojax.django.socialauthentication.models import OpenIdAccount, AuthMeta
from zojax.django.socialauthentication.openid.utils import OpenID
import random


class OpenIdBackend:
    
    def authenticate(self, request=None, identifier=None, openid=None, provider=None):
        if request is None:
            return None
        if not settings.ENABLE_OPENID_AUTH:
            return None
        if not identifier or not openid or not provider:
            return None
        if not isinstance(openid, OpenID):
            return None
        try:
            account = OpenIdAccount.objects.get(identifier = identifier)
            return account.user
        except OpenIdAccount.DoesNotExist:
            #fetch if openid provider provides any simple registration fields
            nickname = None
            email = None
            if openid and openid.sreg:
                email = openid.sreg.get('email')
                nickname = openid.sreg.get('nickname')
            elif openid and openid.ax:
                email = openid.ax.get('email')
                nickname = openid.ax.get('nickname')
            generate_username = False
            if nickname is None:
                generate_username = True
                username =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            else:
                username = nickname

            cnt = 1
            base_username = username
            while User.objects.filter(username = username).count():
                username = "%s-%i" % (base_username, cnt)
                cnt += 1
            user = User.objects.create_user(username, email or '')
            user.save()
    
            #create openid account
            account = OpenIdAccount()
            account.identifier = identifier
            account.user = user
            account.save()
            
            if generate_username:
                username = "openiduser-%i" % account.id
                while User.objects.filter(username = username).count():
                    username += random.choice('abcdefghijklmnopqrstuvwxyz')
                user.username = username
                user.save()
            
            #Create AuthMeta
            auth_meta = AuthMeta(user = user, provider = provider)
            auth_meta.save()
            
            signals.user_registered.send(sender=self.__class__,
                                         user=user,
                                         request=request)

            return user
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None