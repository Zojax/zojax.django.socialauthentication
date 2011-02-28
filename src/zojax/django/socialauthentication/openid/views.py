from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from middleware import OpenIdMiddleware
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE, \
    SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.extensions.ax import AttrInfo, FetchRequest as AXFetchRequest
from openid.extensions.sreg import SRegRequest
from utils import DjangoOpenIDStore, from_openid_response
from yadis import xri
import re
import urlparse

 
 
OPENID_SREG = {"requred": "nickname, email",
               "optional":"postcode, country",
               "policy_url": ""}
 
OPENID_AX = [{"type_uri": "email",
              "count": 1,
              "required": False,
              "alias": "email"},
             {"type_uri": "fullname",
              "count":1 ,
              "required": False,
              "alias": "fullname"},
             {"type_uri": "portrait",
              "count":1 ,
              "required": False,
              "alias": "portrait"},
             {"type_uri": "avatar",
              "count":1 ,
              "required": False,
              "alias": "avatar"}]


def get_trusted_root(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(request.get_host())
    return '%s://%s/' % (protocol, host)


NEXT_URL_RE = re.compile('^/[-\w/]+$')

def is_valid_next_url(next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local 
    # path, not a complete URL.
    return bool(NEXT_URL_RE.match(next))


def openid_login(request):
    identifier = request.POST.get('openid_identifier')
    if not identifier:
        return HttpResponseRedirect(reverse("auth_login"))
    request.session['openid_provider'] = "OpenId"

    return begin(request, identifier)


def google_login(request):
    request.session['openid_provider'] = "Google"
    return begin(request, 'https://www.google.com/accounts/o8/id')
 

def yahoo_login(request):
    request.session['openid_provider'] = "Yahoo"
    return begin(request, 'http://yahoo.com/')


def begin(request, openid_url):
    request.session['request_referer'] = urlparse.urljoin(request.META.get('HTTP_REFERER', ''), '/')
    
    consumer = Consumer(request.session, DjangoOpenIDStore())
 
    try:
        auth_request = consumer.begin(openid_url)
    except DiscoveryFailure:
        return on_failure(request, _('The OpenID was invalid'))
    
    s = SRegRequest()        
    for sarg in OPENID_SREG:
        if sarg.lower().lstrip() == "policy_url":
            s.policy_url = OPENID_SREG[sarg]
        else:
            for v in OPENID_SREG[sarg].split(','):
                s.requestField(field_name=v.lower().lstrip(), required=(sarg.lower().lstrip() == "required"))
    auth_request.addExtension(s)  
    
    axr = AXFetchRequest()
    for i in OPENID_AX:
        axr.add(AttrInfo(i['type_uri'], i['count'], i['required'], i['alias']))
    auth_request.addExtension(axr)
 
    redirect_url = auth_request.redirectURL(get_trusted_root(request),
                                            request.build_absolute_uri(reverse("openid_complete")))
    
    return HttpResponseRedirect(redirect_url)


def complete(request, failure_template='socialauthentication/openid_failure.html'):
    
    consumer = Consumer(request.session, DjangoOpenIDStore())
 
    # JanRain library raises a warning if passed unicode objects as the keys, 
    # so we convert to bytestrings before passing to the library
    query_dict = dict([
        (k.encode('utf8'), v.encode('utf8')) for k, v in request.REQUEST.items()
    ])
 
    openid_response = consumer.complete(query_dict, request.build_absolute_uri(reverse("openid_complete")))
    if openid_response.status == SUCCESS:
        return on_success(request, openid_response.identity_url, openid_response)
    elif openid_response.status == CANCEL:
        return on_failure(request, _('The request was cancelled'), failure_template)
    elif openid_response.status == FAILURE:
        return on_failure(request, openid_response.message, failure_template)
    elif openid_response.status == SETUP_NEEDED:
        return on_failure(request, _('Setup needed'), failure_template)
    else:
        assert False, "Bad openid status: %s" % openid_response.status


def done(request, provider=None):
    """
    When the request reaches here, the user has completed the Openid
    authentication flow. He has authorised us to login via Openid, so
    request.openid is populated.
    After coming here, we want to check if we are seeing this openid first time.
    If we are, we will create a new Django user for this Openid, else login the
    existing openid.
    """
    if not provider:
        provider = request.session.get('openid_provider', '')
    if request.openid:
        #check for already existing associations
        identifier = str(request.openid)
        #authenticate and login
        user = authenticate(request=request, identifier=identifier, openid=request.openid, provider=provider)
        if user:
            login(request, user)
            referer = request.session.get('request_referer')
            next_url = str(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
            if referer:
                next_url = urlparse.urljoin(referer, next_url)
                del request.session['request_referer']
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse("auth_login"))
    else:
        return HttpResponseRedirect(reverse("auth_login"))
    

def on_success(request, identity_url, openid_response):
    if 'openids' not in request.session.keys():
        request.session['openids'] = []
    
    # Eliminate any duplicates
    request.session['openids'] = [
        o for o in request.session['openids'] if o.openid != identity_url
    ]
    request.session['openids'].append(from_openid_response(openid_response))
    
    # Set up request.openids and request.openid, reusing middleware logic
    OpenIdMiddleware().process_request(request)
    
    return HttpResponseRedirect(reverse("openid_done"))
 
 
def on_failure(request, message, failure_template='socialauthentication/openid_failure.html'):
    return render_to_response(failure_template, {
                        'message': message
                        }, RequestContext(request))    
