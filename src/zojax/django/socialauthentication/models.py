from django.db import models
from sorl.thumbnail.fields import ImageWithThumbnailsField, ThumbnailField
from django.contrib.auth.models import User


class AuthMeta(models.Model):
    """Metadata for Authentication"""
    
    def __unicode__(self):
        return '%s - %s' % (self.user, self.provider)
    
    user = models.OneToOneField(User)
    provider = models.CharField(max_length = 200)
    is_email_filled = models.BooleanField(default = False)
    is_profile_modified = models.BooleanField(default = False)
    portrait = models.URLField(null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    location = models.CharField(max_length = 300, null=True, blank=True)
    
    
class OpenIdNonce(models.Model):
    server_url = models.URLField()
    timestamp  = models.IntegerField()
    salt = models.CharField(max_length=50 )
 
    def __unicode__(self):
        return "Nonce: %s" % self.nonce
 
 
class OpenIdAssociation(models.Model):
    server_url = models.TextField(max_length=2047)
    handle = models.CharField(max_length=255)
    secret = models.TextField(max_length=255) # Stored base64 encoded
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.TextField(max_length=64)
 
    def __unicode__(self):
        return "Association: %s, %s" % (self.server_url, self.handle)

    
class OpenIdAccount(models.Model):
    
    user = models.OneToOneField(User, related_name="open_id_account", null=False, blank=False)
    identifier = models.CharField(max_length=200, unique=True, db_index=True)

    def __unicode__(self):
        return unicode(self.identifier)
    
    def __repr__(self):
        return unicode(self.identifier)    


class TwitterAccount(models.Model):
    
    user = models.OneToOneField(User, related_name="twitter_account", null=False, blank=False)
    twitter_id = models.IntegerField(unique=True, db_index=True)
    screen_name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return unicode(self.screen_name)
    
    def __repr__(self):
        return unicode(self.screen_name)    


class FacebookAccount(models.Model):
    
    user = models.OneToOneField(User, related_name="facebook_account", null=False, blank=False)
    facebook_id = models.CharField(max_length = 20, unique = True, db_index = True)

    def __unicode__(self):
        return unicode(self.facebook_id)
    
    def __repr__(self):
        return unicode(self.facebook_id)    

    