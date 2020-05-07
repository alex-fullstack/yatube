from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        error_messages = {
            'username': {
                'required': 'Введите имя пользователя'
            }
        }

    def __init__(self, *args, **kwargs):
        super(CreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].error_messages = {
            'required': 'Введите пароль'
        }
        self.fields['password2'].error_messages = {
            'required': 'Повторите ввод пароля'
        }