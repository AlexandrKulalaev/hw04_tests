from django.db import models

from django.contrib.auth import get_user_model
from django.utils.text import Truncator

     
class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name = 'Заголовок', help_text='Задайте заголовок')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name = 'Описание', max_length=400, 
                                   help_text='Описание группы. Не более 400 символов')
    
    def __str__(self):
        return self.title

User = get_user_model()

class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author') 
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=None, related_name='group', verbose_name='Группа')
    objects = models.Manager()

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        self.text = Truncator(self.text).words(10)
        #return f'{self.text[:15], self.pub_date, self.author, self.group}'
        return self.text[:15]
