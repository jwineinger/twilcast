from django.db import models

class ContactGroup(models.Model):
    """
    Class representing a group of contacts.
    """
    name = models.CharField(max_length=20)
    contacts = models.ManyToManyField('Contact')
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        unique=True,
    )

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ('order',)

PHONE_NUMBER_TYPES = (
    (1, 'Home'),
    (2, 'Cell'),
    (3, 'Work'),
)
class Contact(models.Model):
    """
    Class representing a single contact for a group.
    """
    from django.contrib.localflavor.us import models as us_models
    name = models.CharField(max_length=30)
    phone_number = us_models.PhoneNumberField()
    type = models.PositiveSmallIntegerField(
        choices=PHONE_NUMBER_TYPES,
        default=1,
    )
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.phone_number)
