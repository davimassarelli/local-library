from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre


def index(request):
    """Função View para a home page do site"""

    # Gerador de contagem dos objetos do main
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Livros disponíveis (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # O 'all()' é implícito por padrão
    num_authors = Author.objects.count()

    # Contagem de Generos
    num_genres = Genre.objects.count()

    # Livros que contenham
    num_books_historia = Book.objects.filter(title__icontains='história').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_historia': num_books_historia,
    }

    # Renderizar o HTML template index.html com os dados dentro do contexto variável
    return render(request, 'index.html', context=context)
