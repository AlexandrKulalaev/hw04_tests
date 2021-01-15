from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms  

from posts.models import Post, Group, User


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create(username='author')
        cls.user_other = User.objects.create(username='other')
        
        cls.group = Group.objects.create(
            title = 'Группа для теста',
            slug = 'test_slug',
            description = 'Описание группы'
        )

        cls.post = Post.objects.create(
            text = 'Текст',
            author = cls.user_author,
            group = cls.group,
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client_other = Client()
        self.authorized_client_author = Client()

        self.authorized_client_other.force_login(self.user_other)
        self.authorized_client_author.force_login(self.user_author)


    def test_post_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон. test_views"""
        template_pages_names = {
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_other.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context_index(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(
            reverse('group', kwargs={'slug': 'test_slug'})
        )
        self.assertEqual(response.context.get('group').title, 'Группа для теста')
        self.assertEqual(response.context.get('group').description, 'Описание группы')
        self.assertEqual(response.context.get('group').slug, 'test_slug')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0, 'author')

    def test_username_post_id_page_show_correct_context(self):
        """Шаблон <username> сформирован с правильным контекстом."""
        response = self.authorized_client_other.get(reverse('profile', kwargs={'username': 'author'}))
        post_text_0 = response.context.get('page')[0].text 
        self.assertEqual(post_text_0, PostPagesTest.post.text)
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_author_0, PostPagesTest.post.author)
        post_group_0 = response.context.get('page')[0].group
        self.assertEqual(post_group_0, PostPagesTest.post.group)

    def test_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('post_edit', kwargs={'username':self.user_author, 'post_id': self.post.id}))
        form_fields = {
            "group": forms.fields.ChoiceField, 
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)    

    def test_post_id_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
                reverse('post', kwargs={'username':self.user_author, 'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, 'Текст')
        self.assertEqual(response.context.get('post').author, self.user_author)
        self.assertEqual(response.context.get('post').group, self.group)             

class PaginatorViewsTest(TestCase):

    POSTS_IN_PAGE = 10
    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_other = User.objects.create(username='other')
        
        Post.objects.bulk_create([Post(
            text=f'Тестовое сообщение{i}',
            author=cls.user_other)
            for i in range(cls.POSTS_COUNT)])


    def test_first_page_containse_ten_records(self):
        """Тест паджинатора."""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), self.POSTS_IN_PAGE)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), self.POSTS_COUNT - self.POSTS_IN_PAGE) 
