from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()

    def setUp(self):
        self.guest_client = Client()
        self.user_other = get_user_model().objects.create(username='other')
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user_other)

    def test_about_pages_uses_correct_template(self):
        template_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
