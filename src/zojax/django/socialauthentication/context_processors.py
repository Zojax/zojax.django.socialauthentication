from zojax.django.socialauthentication.settings import ENABLE_OPENID_AUTH,\
    ENABLE_TWITTER_AUTH, ENABLE_FACEBOOK_AUTH, FACEBOOK_API_KEY


def settings(request):
    data = {
        'ENABLE_OPENID_AUTH': ENABLE_OPENID_AUTH,
        'ENABLE_TWITTER_AUTH': ENABLE_TWITTER_AUTH,
        'ENABLE_FACEBOOK_AUTH': ENABLE_FACEBOOK_AUTH,
        'FACEBOOK_API_KEY': FACEBOOK_API_KEY,
    }
    return data