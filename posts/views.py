from django.shortcuts import render
from django.http import HttpResponse
from .models import Posts
from django.db.models import Q

# Create your views here.
def index(request):
    #return HttpResponse("Hello from posts")

    posts = Posts.objects.all()[:10]

    context = {
        'title': 'Search',
        'posts': posts
    }

    return render(request, 'posts/index.html', context)

def details(request, id):
    post = Posts.objects.get(id=id)
    context = {
        'post': post
    }

    return render(request, 'posts/details.html', context)

def search(request):
    template = 'posts/searches.html'
    query = request.GET.get('q')
    results = Posts.objects.filter(Q(title__icontains=query)) 
    context = {
        'posts': results
    }

    return render(request, template, context)
