import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm


#  @login_required
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

    # Número de visitas nesta página, contado com a variável de sessão
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_historia': num_books_historia,
        'num_visits': num_visits,
    }

    # Renderizar o HTML template index.html com os dados dentro do contexto variável
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    """
    context_object_name = 'my_book_list'  # Seu nome para a lista como template variável
    queryset = Book.objects.filter(title__icontains='história')[:5]  # obter 5 livros contendo no título história
    template_name = 'books/my_arbitrary_name_list.html'  # Especifique o nome/localização do seu template
    """


# @login_required - Não aceita o requerimento de login em classes genéricas.
class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Lista Genérica para visualização dos livros atualmente emprestados"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, generic.ListView):
    """Lista genérica para visualização de todos os livros emprestados (somente bibliotecários)"""
    permission_required = 'catalog.can_mark_returned'  # É mais eficaz travar diretamente na urls.py
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Se este é um POST request, então processe os dados do Form
    if request.method == 'POST':

        # Cria um formulario e popula eles com os dados da requisição (binding)
        form = RenewBookForm(request.POST)

        # Verifica se o formulário é valido
        if form.is_valid():
            # processa os dados no form.cleaned_data como requerido (aqui apenas escrevemos isto para o modelo form due_back)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # Redireciona para a nova URL
            return HttpResponseRedirect(reverse('all-borrowed'))

    # Se é um GET (ou outro metodo) cria um formulário padrão
    else:
        proposed_renew_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renew_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
