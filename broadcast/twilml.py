import twilio
from django.core.urlresolvers import reverse

def get_menu_twilml():
    response = twilio.Response()

    # typos are intentional to get Twilio to pronounce correctly
    gather = twilio.Gather(
        action=reverse('handle_menu_response'),
    )
    gather.addSay(
        """
        Press one to enter a quick config code.
        Press two to pick a group to broadcast to.
        """,
        voice=twilio.Say.MAN,
    )
    response.append(gather)
    response.addSay(
        "I'm sorry. I did not hear a selection. Goodbye.",
        voice=twilio.Say.MAN
    )
    response.addHangup()
    return response

def get_group_list_twilml():
    from .contacts.models import ContactGroup
    response = twilio.Response()

    groups = ContactGroup.objects.all().order_by('order')
    groups_text = "".join(["For %s, press %s. " % (g.name, g.order)
                           for g in groups])

    gather = twilio.Gather(
        action=reverse('handle_group_choice_response'),
    )
    gather.addSay(
        """
        At any time, enter the number for the group you wish to broadcast to.
        """ + groups_text,
        voice=twilio.Say.MAN,
    )
    response.append(gather)
    response.addSay(
        "I'm sorry. I did not hear a selection. Goodbye.",
        voice=twilio.Say.MAN
    )
    response.addHangup()
    return response

def get_config_code_twilml():
    """
    After the call is started, Twilio makes a request to this method in order
    to get the TwilML to configure the call.

    This method returns TwilML which instructs Twilio to say a message and and
    record up to one minute from the call recipient. If no audio is recorded
    before a 5 second timeout is reached, another message is played instructing
    the user to initiate another call.
    """
    response = twilio.Response()

    gather = twilio.Gather(
        action=reverse('handle_config_code_response'),
    )
    gather.addSay(
        "Please enter your quick config code.",
        voice=twilio.Say.MAN
    )
    response.append(gather)
    response.addSay(
        "I'm sorry. I did not hear a code. Please call back. Goodbye.",
        voice=twilio.Say.MAN
    )
    response.addHangup()
    return response

def get_recording_twilml(url):
    response = twilio.Response()

    # typos are intentional to get Twilio to pronounce correctly
    response.addSay(
        "After the beep, please reecord a message to be broadcast to all members. This call will end after 60 seconds. Press any key or hang up when you are done.",
        voice=twilio.Say.MAN
    )
    response.addRecord(
        action=url,
        maxLength=60,
        timeout=3,
    )
    response.addSay(
        "I'm sorry. I did not hear a message to record. Please initiate another call. Goodbye.",
        voice=twilio.Say.MAN
    )
    response.addHangup()
    return response

