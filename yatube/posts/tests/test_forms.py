from django.test import TestCase, Client, override_settings
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
import shutil
import tempfile
from django.conf import settings

User = get_user_model()


class PostFormTests(TestCase):
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
            text='Как забыть нормальную жизнь и начать учиться IT',
            group=cls.group,
        )
    
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.group, PostFormTests.group
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostFormTests.user)
        
            
    def test_edit_post(self):
        form_data = {
            'text': 'Измененный старый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk}
        ))
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )