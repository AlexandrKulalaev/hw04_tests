from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model

from .models import Post, Group
from .forms import PostForm


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')

    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator}
    )

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()[:12]

    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'posts': posts, 'page': page, 'paginator': paginator}) 

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            group = form.cleaned_data['group']
            text = form.cleaned_data['text']
            form.save()
            
            return redirect('index')

        return render(request, 'new.html', {'form': form})

    form = PostForm()
    return render(request, 'new.html', {'form': form}) 

User = get_user_model()    
    
def profile(request, username):
    author = User.objects.get(username = username)
    post_list = Post.objects.filter(author = author).select_related('author').order_by('-pub_date')
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'paginator': paginator.count,
        'paginator': paginator
    }
    return render(request, 'profile.html', context)
 
def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    text = Post._meta.get_field("text")
    post = get_object_or_404(Post, id=post_id, author=author)
    count = Post.objects.filter(author=author).select_related('author').count()
    return render(request, 'post.html', {'post': post, 'author': author, 'count': count, 'post_id' : post_id, 'text' : text})

@login_required
def post_edit(request, username, post_id):
    author = User.objects.get(username=username)
    post = get_object_or_404(Post, author=author, id=post_id)

    if request.user != author:
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance = post)
        if form.is_valid():
            post = form.save(commit = False)
            post.save()
            return redirect('post', username=username, post_id=post_id)
    form = PostForm(instance = post)
    return render(request, 'new.html', {'form':form, 'post':post, 'is_edit': True}) 
    