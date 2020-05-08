from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        error_messages = {
            'text': {
                'required': _('Please insert record text')
            }
        }
        widgets = {
            'group': forms.Select(attrs={'class': 'custom-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        error_messages = {
            'text': {
                'required': _('Please insert comment text')
            }
        }
