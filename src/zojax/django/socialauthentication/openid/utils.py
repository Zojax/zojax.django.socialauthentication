from django.conf import settings
from openid.association import Association as OIDAssociation
from openid.extensions.ax import FetchResponse as AXFetchResponse
from openid.extensions.sreg import SRegResponse
from openid.store import nonce as oid_nonce
from openid.store.interface import OpenIDStore
from yadis import xri
from zojax.django.socialauthentication.models import OpenIdAssociation, \
    OpenIdNonce
import time
import base64
import md5
 
 
 

class OpenID:
    def __init__(self, openid, issued, attrs=None, sreg=None, pape=None, ax=None):
        self.openid = openid
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg or {}
        self.pape = pape or {}
        self.ax = ax or {}
        self.is_iname = (xri.identifierScheme(openid) == 'XRI')
    
    def __repr__(self):
        return '<OpenID: %s>' % self.openid
    
    def __str__(self):
        return self.openid
 
class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60 # Six hours
    
    def storeAssociation(self, server_url, association):
        assoc = OpenIdAssociation(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.save()
    
    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = OpenIdAssociation.objects.filter(
                server_url = server_url, handle = handle
            )
        else:
            assocs = OpenIdAssociation.objects.filter(
                server_url = server_url
            )
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append((association.issued, association))
        if not associations:
            return None
        return associations[-1][1]
    
    def removeAssociation(self, server_url, handle):
        assocs = list(OpenIdAssociation.objects.filter(
            server_url = server_url, handle = handle
        ))
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            assoc.delete()
        return assocs_exist
    
    def storeNonce(self, nonce):
        nonce, created = OpenIdNonce.objects.get_or_create(
            nonce = nonce, defaults={'expires': int(time.time())}
        )
    
    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > oid_nonce.SKEW:
            return False
        
        try:
            nonce = OpenIdNonce( server_url=server_url, timestamp=timestamp, salt=salt)
            nonce.save()
        except:
            raise
        else:
            return 1
    
    def getAuthKey(self):
        # Use first AUTH_KEY_LEN characters of md5 hash of SECRET_KEY
        return md5.new(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]
 
 
def from_openid_response(openid_response):
    issued = int(time.time())
 
    openid = OpenID(openid_response.identity_url, issued, openid_response.signed_fields)
 
    if getattr(settings, 'OPENID_SREG', False):
        openid.sreg = SRegResponse.fromSuccessResponse(openid_response)
 
    if getattr(settings, 'OPENID_AX', False):
        openid.ax = AXFetchResponse.fromSuccessResponse(openid_response)
 
    return openid