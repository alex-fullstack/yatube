from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name=_('title'))
    slug = models.SlugField(unique=True, null=False, blank=False, verbose_name=_('slug'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('community')
        verbose_name_plural = _('communities')

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    text = models.TextField(null=False, blank=False, verbose_name=_('text'))
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date published'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author', verbose_name=_('author'))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('community'))
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name=_('image'))

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return str(self.text)


class Comment(models.Model):
    text = models.TextField(null=False, blank=False, verbose_name=_('text'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('author'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('post'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('date of creation'))

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __str__(self):
        return str(self.text)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower', verbose_name=_('user'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name=_('author'))
    follow_on_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date of following'))

    class Meta:
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
