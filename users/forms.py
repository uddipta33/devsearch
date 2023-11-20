from .models import Profile, Skill, Messages
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomeUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']
        labels = {
            'first_name' : 'Full Name'
        }

    def __init__(self, *args, **kwargs):
        super(CustomeUserCreationForm, self).__init__( *args, **kwargs)
        
        # self.fields['title'].widget.attrs.update({'class':'input'})
        # self.fields['description'].widget.attrs.update({'class':'input'})

        for name, field in self.fields.items():
            field.widget.attrs.update({'class':'input'})

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ["user","created"]

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        exclude = ['owner']

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__( *args, **kwargs)
        
        # self.fields['title'].widget.attrs.update({'class':'input'})
        # self.fields['description'].widget.attrs.update({'class':'input'})

        for name, field in self.fields.items():
            field.widget.attrs.update({'class':'input'})

class MessageForm(ModelForm):
    class Meta:
        model = Messages
        fields = ['name','email','subject','body']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__( *args, **kwargs)
        
        # self.fields['title'].widget.attrs.update({'class':'input'})
        # self.fields['description'].widget.attrs.update({'class':'input'})

        for name, field in self.fields.items():
            field.widget.attrs.update({'class':'input'})         