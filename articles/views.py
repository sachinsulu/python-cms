from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse



@ensure_csrf_cookie
@login_required
def article_list(request):
    # Capture the parameter if it exists in the URL
    homepage_param = request.GET.get('homepage')
    
    if homepage_param is not None:
        # Save the choice to the session (namespaced for articles)
        request.session['articles_homepage_filter'] = homepage_param
        # Redirect to the clean URL
        return redirect('article_list')

    # Get the value from session, default to '0' (Inner Page)
    current_filter = request.session.get('articles_homepage_filter', '0')

    # Filtering
    articles = Article.objects.filter(homepage=current_filter).order_by('position')

    return render(request, 'articles/list.html', {
        'list': articles, 
        'current_filter': current_filter
    })


@login_required
def article_create(request):
    session_filter = request.session.get('articles_homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.homepage = homepage 
            article.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Article saved! You can create a new one now.")
                return redirect('article_create')
            elif action == 'save_and_quit':
                return redirect('article_list')
            else:  # 'save'
                messages.success(request, "Article saved!")
                return redirect(reverse('article_edit', args=[article.slug]))
        else:
            print("CREATE FORM ERRORS:", form.errors)
    else:
        form = ArticleForm(initial={'homepage': homepage})

    return render(request, 'articles/form.html', {
        'form': form,
        'homepage': homepage
    })


@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    session_filter = request.session.get('articles_homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.homepage = homepage
            article.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('article_create')
            elif action == 'save_and_quit':
                return redirect('article_list')
            else:  # stay on edit
                return redirect(reverse('article_edit', args=[article.slug]))
        else:
            print("EDIT FORM ERRORS:", form.errors)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/form.html', {
        'form': form,
        'homepage': homepage,
        'is_edit': True,
        'article': article,
    })