from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Profile
from django.conf import settings

def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user = user,
            username = user.username,
            email = user.email,
            name = user.first_name
        )

        subject = "Welcome to devSearch"
        message = "We are glad to have you here..."

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )

def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if (created == False):
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()

post_save.connect(createProfile,sender=User)
post_save.connect(updateUser, sender = Profile)

# @receiver(post_save, sender=Profile)
# def profileUpdates(sender, instance, created, **kwargs):
#     print("Profile updated!!")
#     print("Instance-> ", instance)
#     print("created-> ", created)

# post_save.connect(profileUpdates, sender=Profile)