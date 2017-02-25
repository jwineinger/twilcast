from django.conf.urls.defaults import *

urlpatterns = patterns('twilcast.broadcast.views',
    (r'^$', 'index', {}, 'index'),

    (r'^menu/$', 'configure_menu', {}, 'configure_menu'),
    (r'^menu/handle/$', 'handle_menu_response', {}, 'handle_menu_response'),

    (r'^menu/code/final/$', 'handle_config_code_response', {}, 'handle_config_code_response'),
    (r'^menu/group/final/$', 'handle_group_choice_response', {}, 'handle_group_choice_response'),

    (r'^record/$', 'initiate_call_to_record', {}, 'initiate_call_to_record'),
    (r'^record/configure/$', 'configure_call_to_record', {}, 'configure_call_to_record'),
    (r'^record/status/$', 'statuscallback', {}, 'statuscallback'),
    (r'^record/final/$', 'recordcallback_call_to_record', {}, 'recordcallback_call_to_record'),
    (r'^record/(\d+)/final/$', 'recordcallback_call_to_record', {}, 'recordcallback_for_broadcastcall'),
    
    (r'^playback/(\d+)/$', 'initiate_playback_call', {}, 'initiate_playback_call'),
    (r'^playback/configure/(\d+)/$', 'configure_playback_call', {}, 'configure_playback_call'),
)
