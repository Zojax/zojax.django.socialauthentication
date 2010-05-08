from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from models import TwitterAccount, FacebookAccount, OpenIdAccount, AuthMeta


admin.site.register([TwitterAccount, FacebookAccount, OpenIdAccount, AuthMeta])


class AuthMetaInline(admin.StackedInline):
    model = AuthMeta


class UserAdmin(UserAdmin):
    
    inlines = UserAdmin.inlines + [AuthMetaInline,]

    def provider(user):
        try:
            return user.authmeta.provider
        except AuthMeta.DoesNotExist:
            return _('Default')
    
    def portrait(user):
        try:
            return mark_safe('<img src="%s" width="40px" height="40px" />'%user.authmeta.portrait)
        except AuthMeta.DoesNotExist:
            pass
        
    portrait.allow_tags = True
    
    def avatar(user):
        try:
            return mark_safe('<img src="%s" width="40px" height="40px" />'%user.authmeta.avatar)
        except AuthMeta.DoesNotExist:
            pass
        
    avatar.allow_tags = True
    
    def location(user):
        try:
            return user.authmeta.location
        except AuthMeta.DoesNotExist:
            pass
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', provider, portrait, avatar, location)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

