from email import message
from multiprocessing import context
from os import pardir
import re

from django.shortcuts import render, redirect
from .models import Profile, Skill
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomeUserCreationForm, ProfileForm, SkillForm, MessageForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

# Create your views here.
def loginPage(request):
    page = 'login'
    context = {'page':page}
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == "POST":
        # print(request.POST)
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        # print("username is {} and pw is {}".format(username, password))
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Username doesn't exist")
            # print("Username doesn't exist")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # return redirect('profiles')
            return redirect(request.GET.get('next') if next in request.GET else 'account')
        else:
            messages.error(request, "Username or password is incorrect...")
    return render(request, 'users/login-register.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, "User logged out...")
    return redirect('login')

def registerUser(request):
    page = 'register'
    form = CustomeUserCreationForm()
    context = {'page':page, 'form':form}

    if request.method == "POST":
        form = CustomeUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username =user.username.lower()
            user.save()
            messages.success(request, "User account was created!")
            login(request, user)
            return redirect('edit-account')
        else:
            messages.success(request, "An error occurred during registration!")
    return render(request, 'users/login-register.html', context)

def profiles(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    # all_profiles = Profile.objects.all()
    # all_profiles = Profile.objects.filter(name__icontains = search_query)
    skills = Skill.objects.filter(name__icontains=search_query)
    all_profiles = Profile.objects.distinct().filter(
        Q(name__icontains = search_query) | 
        Q(short_intro__icontains = search_query) |
        Q(skill__in = skills)
    )
    return render(request, 'users/profiles.html', 
        {
            'profiles':all_profiles, 
            'search_query': search_query
        }
    )

def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    return render(request, 'users/user-profile.html', {'profile':profile,
        'topSkills':topSkills, 'otherSkills':otherSkills})

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    projects = profile.project_set.all()
    context = {'profile': profile, 'projects': projects}
    return render(request, 'users/account.html', context)

def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {"form":form}
    return render(request, 'users/profile-form.html', context)

@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()
    context = {'form':form}
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, "Skill was created successfully!")
            return redirect('account')
    return render(request, 'users/skill-form.html', context)

@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    context = {'form':form}
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill was updated successfully!")
            return redirect('account')
    return render(request, 'users/skill-form.html', context)

def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    context = {"object": skill}
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill was deleted successfully!")    
        return redirect('account')
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests':messageRequests, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def viewMessage(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message':message}
    return render(request, 'users/message.html', context)

def createMessage(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            return redirect('user-profile', pk=recipient.id)
    context = {'recipient':recipient, 'form':form}
    return render(request, 'users/message-form.html', context)
    