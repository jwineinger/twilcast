from django.db import models

class CallStatus(models.Model):
    from_number = models.CharField(max_length=12)
    from_zipcode = models.CharField(max_length=5)
    from_state = models.CharField(max_length=2)
    to_number = models.CharField(max_length=12)
    to_zipcode = models.CharField(max_length=5)
    to_state = models.CharField(max_length=2)
    direction = models.CharField(max_length=20)
    call_status = models.TextField(max_length=20)
    call_duration = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField()
    call_sid = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"Status: %s to %s (%ds)" % (
            self.from_number,
            self.to_number,
            self.duration,
        )

    class Meta:
        verbose_name_plural = 'Call Statuses'

class RecordedCall(models.Model):
    from_number = models.CharField(max_length=12)
    from_zipcode = models.CharField(max_length=5)
    from_state = models.CharField(max_length=2)
    to_number = models.CharField(max_length=12)
    to_zipcode = models.CharField(max_length=5)
    to_state = models.CharField(max_length=2)
    direction = models.CharField(max_length=20)
    call_status = models.TextField(max_length=20)
    call_sid = models.CharField(max_length=50)
    recording_url = models.CharField(max_length=200)
    recording_sid = models.CharField(max_length=50)
    recording_duration = models.PositiveSmallIntegerField()
    digits = models.CharField(max_length=10)

    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"Recording: %s to %s (%ds)" % (
            self.from_number,
            self.to_number,
            self.recording_duration,
        )

from django.core.exceptions import ValidationError
import re
non_numeric_re = re.compile(r'\D')
def validate_numeric(value):
    if non_numeric_re.search(value):
        raise ValidationError(u'"%s" contains non numeric values' % value)

class BroadcastCall(models.Model):
    created_by = models.ForeignKey('auth.User', null=True, blank=True)
    contact_groups = models.ManyToManyField(
        'contacts.ContactGroup',
        null=True,
        blank=True,
    )
    access_code = models.CharField(
        max_length=8,
        help_text='The access code needed to record a message for this broadcast.',
        validators=[validate_numeric,],
    )
    recorded_call = models.ForeignKey(RecordedCall, null=True, blank=True)
