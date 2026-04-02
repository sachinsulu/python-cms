# articles/views.py
from django.contrib.auth.decorators import login_required
from users.decorators import requires_perm
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
@requires_perm('articles.view_article')
def article_list(request):
    current_filter = request.GET.get('homepage', '0')
    homepage_bool = (current_filter == '1')
    articles = Article.objects.filter(
        homepage=homepage_bool
    ).order_by('position')

    return render(request, 'articles/list.html', {
        'list': articles,
        'current_filter': current_filter,
    })


@login_required
@requires_perm('articles.add_article')
def article_create(request):
    session_filter = request.GET.get('homepage', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)

            # Handle explicit image removal via the X button
            if request.POST.get('remove_image') == '1':
                article.image = None

            article.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Article saved! You can create a new one now.")
                return redirect('article_create')
            elif action == 'save_and_quit':
                return redirect('article_list')
            else:
                messages.success(request, "Article saved!")
                return redirect(reverse('article_edit', args=[article.slug]))
        else:
            logger.warning("Article create form errors: %s", form.errors)
    else:
        form = ArticleForm(initial={'homepage': homepage})

    return render(request, 'articles/form.html', {
        'form': form,
        'homepage': homepage,
    })


@login_required
@requires_perm('articles.change_article')
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    session_filter = request.GET.get('homepage', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            # Bug fix: do NOT overwrite homepage from session — the form/model owns this value.
            # article.homepage = homepage  ← was silently corrupting homepage field on every edit

            # Handle explicit image removal via the X button
            if request.POST.get('remove_image') == '1':
                article.image = None

            article.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('article_create')
            elif action == 'save_and_quit':
                return redirect('article_list')
            else:
                messages.success(request, "Article saved!")
                return redirect(reverse('article_edit', args=[article.slug]))
        else:
            logger.warning("Article edit form errors: %s", form.errors)
    else:
        # Pre-populate the hidden picker field with the current Media pk
        initial = {}
        if article.image_id:
            initial['image_media'] = article.image_id
        form = ArticleForm(instance=article, initial=initial)

    return render(request, 'articles/form.html', {
        'form': form,
        'homepage': homepage,
        'is_edit': True,
        'article': article,
    })