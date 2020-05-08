from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post, Group, Follow

User = get_user_model()

USERNAME = 'test_user'
PASSWORD = '123456789'
EMAIL = 'test_user@test_user.com'


class ProfileTest(TestCase):

    author_username = 'test_author'
    author_password = '123456789'

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_profile_page_exist(self):
        """Проверка создания страницы автора"""
        User.objects.create_user(
            username=self.author_username, email='test_author@test_author.com', password=self.author_password
        )

        response = self.client.get(f'/{self.author_username}/')

        self.assertEqual(response.status_code, 200, msg='Ошибка перехода на страницу автора')

    def test_profile_page_not_exist(self):
        """Проверка открытия несуществующей страницы автора"""
        response = self.client.get(f'/{self.author_username}/')

        self.assertEqual(
            response.status_code, 404,
            msg='Нет ошибки перехода на несуществующую страницу автора'
        )


class NewPostTest(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)
        cache.clear()

    def test_new_post_create(self):
        """Проверка публикации новой записи"""
        expected_post_text = 'Текст новой записи'
        response = self.client.post('/new/', {'text': expected_post_text}, follow=True)

        self.assertEqual(
            response.redirect_chain, [('/', 302)],
            msg='Нет перенаправления на главную страницу после публикации новой записи'
        )

        self.assertTrue(
            Post.objects.filter(text=expected_post_text).exists(),
            msg="Не удалось опубликовать новую запись"
        )

    def test_new_post_create_fail(self):
        """Проверка перенаправления на главную страницу при попытке опубликовать пост без авторизации"""
        self.client.logout()
        response = self.client.post('/new/', {'text': 'Текст новой записи'}, follow=True)

        self.assertEqual(
            response.redirect_chain, [('/auth/login/?next=/new/', 302)],
            msg='Нет перенаправления на главную страницу при попытке опубликовать пост без авторизации'
        )

    def test_new_post_main_page_publication(self):
        """Проверка публикации новой записи на главной странице"""
        expected_post_text = 'Текст новой записи'
        author = User.objects.get_by_natural_key(USERNAME)
        Post.objects.create(text=expected_post_text, author=author)
        response = self.client.get('/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Вновь созданная запись не отображается на главной странице'
        )

    def test_new_post_profile_page_publication(self):
        """Проверка публикации новой записи на странице автора"""
        expected_post_text = 'Текст новой записи'
        author = User.objects.get_by_natural_key(USERNAME)
        Post.objects.create(text=expected_post_text, author=author)

        response = self.client.get(f'/{USERNAME}/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Вновь созданная запись не отображается на странице автора'
        )

    def test_new_post_details_page_publication(self):
        """Проверка публикации новой записи на странице карточки записи"""
        expected_post_text = 'Текст новой записи'
        author = User.objects.get_by_natural_key(USERNAME)
        post = Post.objects.create(text=expected_post_text, author=author)

        response = self.client.get(f'/{USERNAME}/{post.pk}/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Вновь созданная запись не отображается на странице карточки записи'
        )


class EditPostTest(TestCase):
    new_post_text = 'Текст новой записи'
    new_post = None

    def setUp(self):
        self.client = Client()
        author = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)
        self.new_post = Post.objects.create(text='Текст новой записи', author=author)
        cache.clear()

    def test_new_post_update(self):
        """Проверка редактирования записи"""
        expected_post_text = 'Текст новой записи (ред.)'
        response = self.client.post(f'/{USERNAME}/{self.new_post.pk}/edit/', {'text': expected_post_text}, follow=True)

        self.assertEqual(
            response.redirect_chain, [(f'/{USERNAME}/{self.new_post.pk}/', 302)],
            msg='Нет перенаправления на страницу записи после редактирования записи'
        )

        self.assertContains(
            response, expected_post_text,
            msg_prefix="Не удалось отредактировать запись"
        )

    def test_update_post_on_main(self):
        """Проверка обновления данных записи на главной странице"""
        expected_post_text = 'Текст новой записи (ред.)'
        self.new_post.text = expected_post_text
        self.new_post.save()
        response = self.client.get('/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Отредактированная запись не отображается на главной странице'
        )

    def test_new_post_profile_page_publication(self):
        """Проверка публикации новой записи на странице автора"""
        expected_post_text = 'Текст новой записи'
        self.new_post.text = expected_post_text
        self.new_post.save()

        response = self.client.get(f'/{USERNAME}/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Отредактированная запись не отображается на странице автора'
        )

    def test_new_post_details_page_publication(self):
        """Проверка публикации новой записи на странице карточки записи"""
        expected_post_text = 'Текст новой записи'
        self.new_post.text = expected_post_text
        self.new_post.save()

        response = self.client.get(f'/{USERNAME}/{self.new_post.pk}/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Отредактированная запись не отображается на странице карточки записи'
        )


class NotFoundErrorTest(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_not_found_error_status(self):
        """Проверка возвращения сервером статуса 404, если страница не найдена"""

        response = self.client.get('/unknown_page/')

        self.assertEqual(
            response.status_code, 404,
            msg='Нет ошибки перехода на несуществующую страницу'
        )


class ImagesTest(TestCase):
    new_post = None
    author = None

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)
        cache.clear()

    def test_image_exist_on_post(self):
        """Проверка наличия картинки на странице карточки записи"""
        self.new_post = Post.objects.create(
            text='Текст новой записи',
            author=self.author,
            image='posts/test-image.jpg',
        )
        response = self.client.get(f'/{self.author.username}/{self.new_post.pk}/')

        self.assertContains(
            response, 'img',
            msg_prefix='Изображение не отображается на странице карточки записи'
        )

    def test_image_exist_on_profile(self):
        """Проверка наличия картинки на странице автора"""
        self.new_post = Post.objects.create(
            text='Текст новой записи',
            author=self.author,
            image='posts/test-image.jpg',
        )
        response = self.client.get(f'/{self.author.username}/')

        self.assertContains(
            response, 'img',
            msg_prefix='Изображение не отображается на странице автора'
        )

    def test_image_exist_on_group(self):
        """Проверка наличия картинки на странице сообщества"""
        group = Group.objects.create(
            title='Новая группа',
            slug='public',
        )
        self.new_post = Post.objects.create(
            text='Текст новой записи',
            author=self.author,
            group=group,
            image='posts/test-image.jpg',
        )
        response = self.client.get('/group/public/')

        self.assertContains(
            response, 'img',
            msg_prefix='Изображение не отображается на странице сообщества'
        )

    def test_image_exist_on_index(self):
        """Проверка наличия картинки на главной странице"""
        self.new_post = Post.objects.create(
            text='Текст новой записи',
            author=self.author,
            image='posts/test-image.jpg',
        )
        response = self.client.get('/')

        self.assertContains(
            response, 'img',
            msg_prefix='Изображение не отображается на главной странице'
        )


class CacheTest(TestCase):
    new_post = None
    author = None

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)
        self.new_post = Post.objects.create(text='Текст новой записи', author=self.author)
        cache.clear()

    def test_index_page_caching(self):
        """Проверка кэширования данных главной страницы"""
        expected_post_text = 'Текст новой записи'
        self.client.get('/')
        self.new_post.text = 'Измененная запись'
        self.new_post.save()
        response = self.client.get('/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Данные на главной странице не кэшируются'
        )

        cache.clear()
        response = self.client.get('/')

        expected_post_text = 'Измененная запись'
        self.assertContains(
            response, expected_post_text,
            msg_prefix='Данные на главной странице не обновляются после сброса кэша'
        )


class FollowTest(TestCase):
    author = None
    user = None

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.author = User.objects.create_user(username='test_author', email='test_author@test_author.com', password=PASSWORD)
        self.client.login(username=USERNAME, password=PASSWORD)
        cache.clear()

    def test_follow(self):
        """Проверка подписки на ленту автора"""
        self.client.get(f'/{self.author.username}/follow/')

        self.assertTrue(
            Follow.objects.filter(author=self.author, user=self.user).exists(),
            msg="Нет подписки на ленту автора"
        )

    def test_unfollow(self):
        """Проверка отписки от ленты автора"""
        Follow.objects.create(author=self.author, user=self.user)

        self.client.get(f'/{self.author.username}/unfollow/')

        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(author=self.author, user=self.user)

    def test_new_post_public_on_follow_page(self):
        """Проверка публикации новой записи в ленте подписчика"""
        expected_post_text = 'Текст новой записи'
        Post.objects.create(text=expected_post_text, author=self.author)
        self.client.get(f'/{self.author.username}/follow/')
        response = self.client.get('/follow/')

        self.assertContains(
            response, expected_post_text,
            msg_prefix='Вновь созданная запись не отображается в ленте подписчика'
        )

    def test_new_post_not_public_on_follow_page(self):
        """Проверка отсуствия публикации новой записи в ленте не подписанного пользователя"""
        expected_post_text = 'Текст новой записи'
        Post.objects.create(text=expected_post_text, author=self.author)
        response = self.client.get('/follow/')

        self.assertNotContains(
            response, expected_post_text,
            msg_prefix="Вновь созданная запись отображается в ленте не подписанного пользователя"
        )


class CommentsTest(TestCase):
    author = None

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        cache.clear()

    def test_add_comment(self):
        """Проверка добавления комментария авторизованным пользователем"""
        self.client.login(username=USERNAME, password=PASSWORD)
        expected_comment_text = 'Текст комментария'
        post = Post.objects.create(text='Текст новой записи', author=self.author)
        self.client.post(f'/{USERNAME}/{post.pk}/comment/', {'text': expected_comment_text})
        response = self.client.get(f'/{USERNAME}/{post.pk}/')

        self.assertContains(
            response, expected_comment_text,
            msg_prefix='Вновь созданный комментарий не отображается на странице записи'
        )

    def test_add_comment_failure(self):
        """Проверка добавления комментария неавторизованным пользователем"""
        post = Post.objects.create(text='Текст новой записи', author=self.author)
        response = self.client.post(f'/{USERNAME}/{post.pk}/comment/', {'text': 'Текст комментария'}, follow=True)

        self.assertEqual(
            response.redirect_chain, [(f'/auth/login/?next=/{USERNAME}/{post.pk}/comment/', 302)],
            msg='Нет перенаправления на страницу авторизации после попытки публикации нового комментария'
        )
