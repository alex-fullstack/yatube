from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].widget.attrs.update({'class': 'custom-select'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        error_messages = {
            'text': {
                'required': _('Please insert record text')
            }
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
