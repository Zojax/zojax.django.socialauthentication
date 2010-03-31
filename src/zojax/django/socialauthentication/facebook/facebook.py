from zojax.django.socialauthentication.settings import FACEBOOK_API_KEY, \
    FACEBOOK_API_SECRET
import md5
import simplejson
import time
import urllib
import datetime


REST_SERVER = 'http://api.facebook.com/restserver.php'


def getFacebookSignatureHash(valuesDict, apiKey, apiSecret, isCookieCheck=False):
    signature_keys = []
    for key in sorted(valuesDict.keys()):
        if (isCookieCheck and key.startswith(apiKey + '_')):
            signature_keys.append(key)
        elif (isCookieCheck is False):
            signature_keys.append(key)
    if (isCookieCheck):
        signature_string = ''.join(['%s=%s' % (x.replace(apiKey + '_',''), valuesDict[x]) for x in signature_keys])
    else:
        signature_string = ''.join(['%s=%s' % (x, valuesDict[x]) for x in signature_keys])
    signature_string = signature_string + apiSecret

    return md5.new(signature_string).hexdigest()


def getFacebookUserId(request):
    cookies = request.COOKIES
    if FACEBOOK_API_KEY not in cookies:
        return None
    signatureHash = getFacebookSignatureHash(cookies, FACEBOOK_API_KEY, FACEBOOK_API_SECRET, True)
    if signatureHash != cookies[FACEBOOK_API_KEY]:
        return None
    if(datetime.datetime.fromtimestamp(float(cookies[FACEBOOK_API_KEY+'_expires'])) <= datetime.datetime.now()):
        return None
    return int(cookies[FACEBOOK_API_KEY + '_user'])


def getFacebookUserInfo(facebook_id):
    params = {
        'method': 'Users.getInfo',
        'api_key': FACEBOOK_API_KEY,
        'call_id': time.time(),
        'v': '1.0',
        'uids': facebook_id,
        'fields': 'first_name,last_name,username,pic_big,pic_small,current_location,hometown_location',
        'format': 'json',
    }
    params['sig'] = getFacebookSignatureHash(params, FACEBOOK_API_KEY, FACEBOOK_API_SECRET)
    params = urllib.urlencode(params)
    response  = simplejson.load(urllib.urlopen(REST_SERVER, params))
    result = response[0]
    return result
