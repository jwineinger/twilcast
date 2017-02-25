from django.http import HttpResponse
from django.db.models import get_model

import twilio

class TwilMLResponse(object):
    """
    A class to be used as a decorator for views which should return TwiML.
    The decorated view should return either a twilio.Response object or None.
    If None is returned, the decorator will return a proper empty TwilML
    response, otherwise it will output the proper XML header followed by the
    TwilML.
    """
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        response = self.f(*args, **kwargs)

        if isinstance(response, HttpResponse):
            return response

        if response is None:
            response = twilio.Response()

        return HttpResponse(
            u"""<?xml version="1.0" encoding="UTF-8"?>\n""" + unicode(response),
            mimetype='text/xml'
        )

class PhoneNumberProtected(object):
    """
    A class to be used as a decorator for views which should be protected by
    phone number.  This decorator will look up the incoming phone number
    against the phone_number column of the UserProfile table to determine if
    call should be accepted or rejected.
    """
    def __init__(self, f):
        self.f = f

    def get_reject_response(self):
        response = twilio.Response()

        response.append(twilio.Reject(
            reason=twilio.Reject.BUSY
        ))
        return HttpResponse(
            u"""<?xml version="1.0" encoding="UTF-8"?>""" + unicode(response),
            mimetype='text/xml'
        )

    def get_associated_user(self, number):
        UserProfile = get_model('profiles','UserProfile')

        import re
        digits = ''.join(re.findall(r'\d', number))
        if len(digits) > 10:
            digits = digits[-10:]

        try:
            profile = UserProfile.objects.select_related('user').get(
                phone_number_digits=digits
            )
            return profile.user
        except UserProfile.DoesNotExist:
            return False

    def __call__(self, request, *args, **kwargs):
        number = request.POST.get('From', '')
        user = self.get_associated_user(number)
        if not request.POST or not user:
            return self.get_reject_response()
        else:
            response = self.f(request, *args, **kwargs)
            response.set_cookie('user_id', user.pk)
            return response
