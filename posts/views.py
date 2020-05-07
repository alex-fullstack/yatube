from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, ListView, View
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.utils.decorators import classonlymethod
from django.http import HttpResponseRedirect

from .forms import PostForm, CommentForm
from .mixins import SummaryViewMixin, AuthorMixin, PostListViewMixin, ClearCacheMixin
from .models import Post, Group, Comment, Follow

User = get_user_model()


class IndexView(PostListViewMixin):
    template_name = 'index.html'

    @classonlymethod
    def as_view(self, **kwargs):
        return cache_page(20, key_prefix='index_page')(super(IndexView, self).as_view(**kwargs))

    def get_queryset(self):
        return Post.objects.order_by('-pub_date')


class FollowView(LoginRequiredMixin, PostListViewMixin):
    template_name = 'follow.html'

    @property
    def authors(self):
        follows = Follow.objects.filter(user=self.request.user)
        return [item.author for item in follows]

    def get_queryset(self):
        return Post.objects.filter(author__in=self.authors).order_by('-pub_date')


class ProfileFollowView(LoginRequiredMixin, AuthorMixin, View):
    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.kwargs['username']})

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user != self.author:
            Follow.objects.get_or_create(user=user, author=self.author)
        return HttpResponseRedirect(self.get_success_url())


class ProfileUnfollowView(LoginRequiredMixin, AuthorMixin, View):
    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.kwargs['username']})

    def get(self, request, *args, **kwargs):
        following = get_object_or_404(Follow, user=self.request.user, author=self.author)
        following.delete()
        return HttpResponseRedirect(self.get_success_url())


class GroupView(PostListViewMixin):
    template_name = 'group.html'
    _group = None

    @property
    def group(self):
        if not self._group or self._group.slug != self.kwargs['slug']:
            self._group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self._group

    def get_queryset(self):
        return Post.objects.filter(group=self.group).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class ProfileView(SummaryViewMixin, PostListViewMixin):
    template_name = 'profile.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.author).order_by('-pub_date')


class ReadPostView(SummaryViewMixin, DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'post.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = {
            'items': Comment.objects.filter(post_id=self.kwargs['post_id']),
            'form': CommentForm(initial={'post': self.object})
        }
        return context


class UpdatePostView(LoginRequiredMixin, ClearCacheMixin, AuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'new.html'
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        if self.author != self.request.user:
            return redirect('post', username=kwargs['username'], post_id=kwargs['post_id'])
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post', kwargs={'username': self.author, 'post_id': self.kwargs['post_id']})

    def form_valid(self, form):
        form.instance.author = self.author
        return super(UpdatePostView, self).form_valid(form)


class CreatePostView(LoginRequiredMixin, ClearCacheMixin, CreateView):
    form_class = PostForm
    success_url = reverse_lazy('index')
    template_name = 'new.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CreatePostView, self).form_valid(form)


class CreateCommentView(LoginRequiredMixin, ClearCacheMixin, CreateView):
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('post', kwargs={'username': self.kwargs['username'], 'post_id': self.kwargs['post_id']})

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super(CreateCommentView, self).form_valid(form)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
