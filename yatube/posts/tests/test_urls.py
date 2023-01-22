from django.test import TestCase, Client
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
from django.core.cache import cache


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tanya')
        cls.group = Group.objects.create(
            title='Группа вредителей',
            slug='fedo',
            description='волчья стая'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Как забыть нормальную жизнь и начать учиться IT'
        )
    
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

