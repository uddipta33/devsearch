from multiprocessing import context
from pydoc import describe
from unittest import result
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

projectList = [
    {
        "id": '1',
        "title": "Ecommerce Website",
        "description": "Fully functional ecommerce website",
    },
       {
        "id": '2',
        "title": "Portfolio Website",
        "description": "Fully functional Portfolio website",
    },
       {
        "id": '3',
        "title": "Social Network",
        "description": "Fully functional Social Network website",
    },
]
# Create your views here.
def projects(request):
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    # projects = Project.objects.all()
    tags = Tag.objects.filter(name__icontains=search_query)
    projects = Project.objects.distinct().filter(
        Q(title__icontains=search_query) |
        Q(description__icontains = search_query) |
        Q(owner__name__icontains = search_query) |
        Q(tags__in = tags)
    )

    page = request.GET.get('page')
    results = 3
    paginator = Paginator(projects, results)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        projects = paginator.page(page)
    
    left_range = int(page) - 4
    if left_range < 1:
        left_range = 1
    
    right_range = int(page) + 5
    if right_range > paginator.num_pages:
        right_range = paginator.num_pages + 1
    
    custom_range = range(left_range, right_range)
    
    context = {'projects':projects, 'search_query':search_query, 'paginator':paginator,
        'custom_range':custom_range}
    return render(request, 'projects/projects.html', context)
    
@login_required(login_url='login')
def project(request, pk):
    # projectObj = None
    # for i in projectList:
    #     if i.get('id') == pk:
    #         projectObj = i
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()
    profile = request.user.profile
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = profile
            review.project = projectObj
            review.save()
            
            projectObj.getVotes
            messages.success(request, "Review submitted sucessfully")
            return redirect('project', pk=projectObj.id)
    return render(request, 'projects/single-project.html', {'project':projectObj, 'form':form})

@login_required(login_url='login')
def createProject(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        # print("form---->", form)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            return redirect('projects')

    form  = ProjectForm()
    context = {'form':form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def updateProject(request, pk):
    profile = request.user.profile
    # project = Project.objects.get(id=pk)
    project = profile.project_set.get(id=pk)
    form  = ProjectForm(instance=project)
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        # print("form---->", form)
        if form.is_valid():
            form.save()
            return redirect('projects')

    
    context = {'form':form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def deleteProject(request, pk):
    profile = request.user.profile
    # project = Project.objects.get(id=pk)
    project = profile.project_set.get(id=pk)
    if request.method == "POST":
        project.delete()
        return redirect('projects')
    context = {'object':project} 
    return render(request, "delete_template.html", context)
