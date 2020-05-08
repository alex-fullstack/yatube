from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.core.cache import cache

from .models import Post, Follow

User = get_user_model()


class AuthorMixin(object):
    _author = None

    @property
    def author(self):
        if not self._author or self._author.username != self.kwargs['username']:
            self._author = get_object_or_404(User, username=self.kwargs['username'])
        return self._author


class SummaryViewMixin(AuthorMixin, TemplateResponseMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['posts_count'] = Post.objects.filter(author=self.author).count()
        followers = Follow.objects.filter(author=self.author)
        if followers.exists():
            context['followers'] = followers
            following = followers.filter(user=self.request.user)
            if following.count() == 1:
                context['following'] = following[0]
        return context


class PostListViewMixin(ListView):
    model = Post
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        context['page'] = context['paginator'].get_page(page_number)
        return context


class ClearCacheMixin(FormMixin):
    def form_valid(self, form):
        cache.clear()
        return super(ClearCacheMixin, self).form_valid(form)
