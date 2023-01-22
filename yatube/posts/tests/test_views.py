from django.test import TestCase, Client
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms


User = get_user_model()

POST_IN_FIRST_PAGE = 10
POST_IN_SECOND_PAGE = 3


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(author=cls.user,
                                    text='Тестовый текст',
                                    group=cls.group)
    
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
    
    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile', args=[self.user.username]),
            'posts/post_detail.html': reverse('posts:post_detail', args=[self.post.id]),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/create_post.html': reverse('posts:post_edit', args=[self.post.id]),
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        first_post = response.context.get('page_obj')[0]
        self.assertEqual(first_post.id, self.post.id)
        self.assertEqual(first_post.text, self.post.text)
        self.assertEqual(first_post.author.username, self.user.username)
        self.assertEqual(first_post.author.get_full_name(), self.user.get_full_name())

    def test_group_list_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_post = response.context.get('page_obj')[0]
        self.assertEqual(first_post.id, self.post.id)
        self.assertEqual(first_post.text, self.post.text)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(first_post.group.title, self.group.title)
        self.assertEqual(first_post.group.description, self.group.description)
        self.assertEqual(first_post, self.post)

    def test_post_create_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly_user2(self):
        """Пост при создании не добавляется другому пользователю
           Но виден на главной и в группе"""
        group2 = Group.objects.create(title='Тестовая группа 2',
                                      slug='test_group2')
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count, 'поста нет в другой группе')
        self.assertNotIn(post, profile,
                         'поста нет в группе другого пользователя')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = get_user_model().objects.create(username='User')
        for i in range(13):
            Post.objects.create(author=cls.user, text=f'Текст{i}')

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))

        self.assertEqual(len(response.context.get('page_obj').object_list), POST_IN_FIRST_PAGE)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')

        self.assertEqual(len(response.context.get('page_obj').object_list), POST_IN_SECOND_PAGE)