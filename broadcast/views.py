from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

import twilio, json
from decorators import TwilMLResponse, PhoneNumberProtected

import twilml

def index(request):
    from django.views.generic.simple import direct_to_template
    return direct_to_template(request, 'broadcast/base.html')

def initiate_call(request, **kwargs):
    """
    Initiate a Twilio call using the parameters in kwargs.  The method should
    check that the required parameters are given.
    """
    from django.conf import settings
    assert 'From' in kwargs, "'From' is required when initiating a call."
    assert 'To' in kwargs, "'To' is required when initiating a call."
    assert 'Url' in kwargs, "'Url' is required when initiating a call."

    account = twilio.Account(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_ACCOUNT_TOKEN,
    )

    url = "/%s/Accounts/%s/Calls" % (
        settings.TWILIO_API_VERSION,
        settings.TWILIO_ACCOUNT_SID,
    )
    host = "http://%s" % request.META['HTTP_HOST']
    account.request(url, 'POST', kwargs)

@csrf_exempt
@PhoneNumberProtected
@TwilMLResponse
def configure_menu(request):
    return twilml.get_menu_twilml()

@csrf_exempt
@TwilMLResponse
def handle_menu_response(request):
    choice = request.POST.get('Digits', '')

    if choice == '1':
        response = twilml.get_config_code_twilml()
    elif choice == '2':
        response = twilml.get_group_list_twilml()
    else:
        response = twilml.get_menu_twilml()

    return response

@csrf_exempt
@TwilMLResponse
def handle_config_code_response(request):
    """
    This view should lookup the access code entered by the user.
    """
    from models import BroadcastCall
    print "Digits: %s" % request.POST.get('Digits')
    try:
        bc = BroadcastCall.objects.get(
            access_code=request.POST.get('Digits', ''),
        )
        print "Got BC"
    except BroadcastCall.DoesNotExist:
        bc = None
        print "No BC found"

    if bc is None:
        response = twilio.Response()
        response.addSay(
            "Sorry, the code you entered is not valid. Goodbye.",
            voice=twilio.Say.MAN
        )
        response.addHangup()
    else:
        response = twilml.get_recording_twilml(
            reverse('recordcallback_for_broadcastcall', args=[bc.pk])
        )
    return response

@csrf_exempt
@TwilMLResponse
def handle_group_choice_response(request):
    from models import BroadcastCall
    from .contacts.models import ContactGroup
    from django.db.models import get_model

    choice = request.POST.get('Digits', '')
    group = ContactGroup.objects.filter(
        order=choice
    )

    if group:
        user = get_model('auth','User').objects.get(
            pk=request.COOKIES['user_id']
        )
        bc = BroadcastCall.objects.create(
            created_by_id=request.COOKIES['user_id'],
        )
        # M2M has to be set after the BC is created
        bc.contact_groups = [g for g in group]

        response = twilml.get_recording_twilml(
            reverse('recordcallback_for_broadcastcall', args=[bc.pk])
        )
    else:
        response = twilml.get_group_list_twilml()
        response.verbs.insert(
            0,
            twilio.Say(
                "Invalid choice. ",
                voice=twilio.Say.MAN
            )
        )
    return response

def initiate_call_to_record(request):
    """
    Initiate a call to the specified number. When the call is complete, Twilio
    will POST to the StatusCallback URL to notify this application the call has
    ended.
    """
    import urllib2
    from django.conf import settings

    host = "http://%s" % request.META['HTTP_HOST']
    try:
        initiate_call(
            request,
            **{
                'From':settings.OUTGOING_NUMBER,
                'To':request.GET.get('number'),
                'Url':"%s%s" % (host, reverse('configure_call_to_record')),
                'StatusCallback':"%s%s" % (host, reverse('statuscallback')),
                'Timeout':10,
            }
        )
    except urllib2.HTTPError, e:
        raise Exception(e.read())
    return HttpResponse("Initiating call")

@csrf_exempt
@TwilMLResponse
def configure_call_to_record(request):
    """
    After the call is started, Twilio makes a request to this method in order
    to get the TwilML to configure the call.

    This method returns TwilML which instructs Twilio to say a message and and
    record up to one minute from the call recipient. If no audio is recorded
    before a 5 second timeout is reached, another message is played instructing
    the user to initiate another call.
    """
    return twilml.get_recording_twilml(
        reverse('recordcallback_call_to_record')
    )

@csrf_exempt
@TwilMLResponse
def statuscallback(request):
    """
    Twilio will make a request to this method with the "StatusCallback"
    parameter with CallStatus variable set to 'in-progress' for successful and
    completed calls, 'no-answer' for calls that were not answered, 'busy' if
    the line is busy, or 'failed if the call could not be completed as dialed.
    """
    from models import CallStatus

    kwargs = {
        'from_number': request.POST.get('From',''),
        'from_zipcode': request.POST.get('FromZip', ''),
        'from_state': request.POST.get('FromState', ''),
        'to_number'  : request.POST.get('To', ''),
        'to_zipcode': request.POST.get('ToZip', ''),
        'to_state': request.POST.get('ToState', ''),
        'direction': request.POST.get('Direction', ''),
        'call_status': request.POST.get('CallStatus', ''),
        'call_duration': request.POST.get('CallDuration', 0),
        'duration': request.POST.get('Duration', 0),
        'call_sid': request.POST.get('CallSid', ''),
    }

    CallStatus.objects.create(**kwargs)

@csrf_exempt
@TwilMLResponse
def recordcallback_call_to_record(request, broadcast_call_id=None):
    """
    This callback is POST'ed to by Twilio with details of the recorded message
    from the "click-to-call" call.
    """
    from models import RecordedCall, BroadcastCall

    kwargs = {
        'from_number': request.POST.get('From',''),
        'from_zipcode': request.POST.get('FromZip', ''),
        'from_state': request.POST.get('FromState', ''),
        'to_number'  : request.POST.get('To', ''),
        'to_zipcode': request.POST.get('ToZip', ''),
        'to_state': request.POST.get('ToState', ''),
        'direction': request.POST.get('Direction', ''),
        'call_status': request.POST.get('CallStatus', ''),
        'call_sid': request.POST.get('CallSid', ''),
        'recording_url': request.POST.get('RecordingUrl', ''),
        'recording_sid': request.POST.get('RecordingSid', ''),
        'recording_duration': request.POST.get('RecordingDuration', 0),
        'digits': request.POST.get('Digits', ''),
    }

    recorded_call = RecordedCall.objects.create(**kwargs)

    if broadcast_call_id:
        try:
            bc = BroadcastCall.objects.select_related('contact_groups').get(pk=broadcast_call_id)
            bc.recorded_call = recorded_call
            bc.save()

            for group in bc.contact_groups.all():
                print "Broadcasting to group %s" % group.name
                for contact in group.contacts.all():
                    print "\t%s at %s" % (contact.name, contact.phone_number)
                    broadcast_recorded_call(request, recorded_call.pk, contact.phone_number)
        except BroadcastCall.DoesNotExist, e:
            pass
            import traceback
            traceback.print_exc()

def broadcast_recorded_call(request, recordedcall_id, to_number):
    """
    Initiate a call to the specified number. When the call is complete, Twilio
    will POST to the StatusCallback URL to notify this application the call has
    ended.
    """
    import urllib2
    from models import RecordedCall
    from django.conf import settings

    host = "http://%s" % request.META['HTTP_HOST']
    try:
        initiate_call(
            request,
            **{
                'From':settings.OUTGOING_NUMBER,
                'To': to_number,
                'Url':"%s%s" % (host, reverse('configure_playback_call', args=[recordedcall_id])),
                'StatusCallback':"%s%s" % (host, reverse('statuscallback')),
                'Timeout':20,
            }
        )
    except urllib2.HTTPError, e:
        raise Exception(e.read())
    return HttpResponse("Initiating call")

def initiate_playback_call(request, recordedcall_id):
    """
    Initiate a call to the specified number. When the call is complete, Twilio
    will POST to the StatusCallback URL to notify this application the call has
    ended.
    """
    import urllib2
    from django.shortcuts import get_object_or_404
    from models import RecordedCall
    from django.conf import settings

    recorded_call = get_object_or_404(RecordedCall, pk=recordedcall_id)
    host = "http://%s" % request.META['HTTP_HOST']
    try:
        initiate_call(
            request,
            **{
                'From':settings.OUTGOING_NUMBER,
                'To':request.GET.get('number'),
                'Url':"%s%s" % (host, reverse('configure_playback_call', args=[recordedcall_id])),
                'StatusCallback':"%s%s" % (host, reverse('statuscallback')),
                'Timeout':10,
            }
        )
    except urllib2.HTTPError, e:
        raise Exception(e.read())
    return HttpResponse("Initiating call")

@csrf_exempt
@TwilMLResponse
def configure_playback_call(request, recordedcall_id):
    """
    After the call is started, Twilio makes a request to this method in order
    to get the TwilML to configure the call.

    This method returns TwilML which instructs Twilio to playback a previously
    recorded message.
    """
    from django.shortcuts import get_object_or_404
    from models import RecordedCall
    recorded_call = get_object_or_404(RecordedCall, pk=recordedcall_id)

    response = twilio.Response()
    response.addPlay(recorded_call.recording_url)
    response.addHangup()
    return response
