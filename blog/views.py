# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from users.decorators import requires_perm
from django.contrib import messages
from django.urls import reverse


@login_required
@requires_perm('blog.view_blog')
def blog_list(request):
    blogs = Blog.objects.all().order_by('position')
    return render(request, 'blog/list.html', {'list': blogs})


@login_required
@requires_perm('blog.add_blog')
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)

            if request.POST.get('remove_image') == '1':
                blog.image = None
            if request.POST.get('remove_banner_image') == '1':
                blog.banner_image = None

            blog.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_quit':
                return redirect('blog_list')
            else:
                messages.success(request, "Blog saved!")
                return redirect(reverse('edit_blog', args=[blog.slug]))
    else:
        form = BlogForm()

    return render(request, 'blog/form.html', {'form': form})


@login_required
@requires_perm('blog.change_blog')
def edit_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)

            if request.POST.get('remove_image') == '1':
                blog.image = None
            if request.POST.get('remove_banner_image') == '1':
                blog.banner_image = None

            blog.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_quit':
                return redirect('blog_list')
            else:
                messages.success(request, "Blog saved!")
                return redirect(reverse('edit_blog', args=[blog.slug]))
    else:
        initial = {}
        if blog.image_id:
            initial['image_media'] = blog.image_id
        if blog.banner_image_id:
            initial['banner_image_media'] = blog.banner_image_id
        form = BlogForm(instance=blog, initial=initial)

    return render(request, 'blog/form.html', {
        'form':    form,
        'is_edit': True,
        'blog':    blog,
    })