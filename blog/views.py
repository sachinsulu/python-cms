from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog
from .forms import BlogForm
from django.contrib.auth.decorators import login_required


@login_required
def blog_list(request):
    homepage_param = request.GET.get('homepage')
    
    if homepage_param is not None:
        # Save the choice to the session (namespaced for blog)
        request.session['blog_homepage_filter'] = homepage_param
        return redirect('blog_list')

    # Get the value from session, default to '0' (Inner Page)
    current_filter = request.session.get('blog_homepage_filter', '0')

    # Filtering
    blog = Blog.objects.filter(homepage=current_filter).order_by('position')

    return render(request, 'blog/list.html', {
        'list': blog,
        'current_filter': current_filter
    })


@login_required
def create_blog(request):
    session_filter = request.session.get('blog_homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(initial={'homepage': homepage})

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage
    })


@login_required
def edit_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    session_filter = request.session.get('blog_homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage,
        'is_edit': True
    })