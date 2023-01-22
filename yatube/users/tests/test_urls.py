from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        """Создаем клиент гостя и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='leo')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена."""
        templates_pages_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={
                        'uidb64': 'NA', 'token': '5u2-61df9f91c57dffda7348'
                    }): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)