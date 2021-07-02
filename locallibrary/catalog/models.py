import uuid

from django.db import models
from django.urls import reverse  # Utilizado para gerarar URLs revertendo o URL patterns.


class Genre(models.Model):
    """Modelo representando o gênero do livro"""
    name = models.CharField(
        max_length=200,
        help_text='Insira o gênero do livro (ex. Ficção científica)',
    )

    def __str__(self):
        """String para representar o objeto Modelo"""
        return self.name


class Language(models.Model):
    """Modelo representando a Linguagem (ex. Inglês, Francês, Japonês, etc.)"""
    name = models.CharField(
        max_length=200,
        help_text='Insira a linguagem do livro (ex. Inglês, Francês, Japonês, etc.)'
    )

    def __str__(self):
        """String para representar o objeto do Modelo"""
        return self.name


class Book(models.Model):
    """Modelo representando um livro (mas não especificamente a cópia de um livro)."""
    title = models.CharField(max_length=200)

    # Foring Key usada pois um livro pode ter apenas um autor, mas autores podem ter multiplos livros
    # Autor como string em vez de objeto pois ainda não o declaramos no arquivo
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Digite uma breve descrição do livro')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Caracteres <a href="https://www.isbn-international'
                                                             '.org/content/what-isbn">Número ISBN</a>')

    # ManyToManyField usada pois o genero pode conter vários livros. Livros podem ser de vários generos.
    # A classe Genero já foi definida então conseguimos especificar o objeto acima.
    genre = models.ManyToManyField(Genre, help_text='Selecione um genero para este livro')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """Cria uma string para o gênero. Requerido para aparecer em Admin"""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def __str__(self):
        """String para representar o objeto Modelo"""
        return self.title

    def get_absolute_url(self):
        """Retorna a url para acessar os detalhes atribuidos ao livro"""
        return reverse('book-detail', args=[str(self.id)])

from datetime import date
from django.contrib.auth.models import User


class BookInstance(models.Model):
    """Modelo representando uma cópia específica de um livro (ex. que pode ser emprestado da biblioteca)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Id única para este livro em toda a '
                                                                          'biblioteca')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('m', 'Manutenção'),
        ('o', 'Emprestado'),
        ('a', 'Disponível'),
        ('r', 'Reservado'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Disponibilidade de Livro',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "marcar como devolvido"),)

    def __str__(self):
        """String para representar o objeto do Modelo"""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Modelo representando o autor"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Retorna a url para acessar particularmente o author instanciado"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String para representar o objeto do Modelo"""
        return f'{self.last_name}, {self.first_name}'

