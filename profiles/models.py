from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    from django.contrib.localflavor.us import models as us_models
    user = models.ForeignKey(User, unique=True)
    phone_number = us_models.PhoneNumberField()
    phone_number_digits = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        if self.phone_number:
            import re
            digits = ''.join(re.findall(r'\d', self.phone_number))
            if len(digits) > 10:
                digits = digits[-10:]
            self.phone_number_digits = digits
        super(UserProfile, self).save(*args, **kwargs)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
