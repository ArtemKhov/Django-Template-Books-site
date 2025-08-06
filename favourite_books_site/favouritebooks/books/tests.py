from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from books.models import Book
from django.contrib.auth import get_user_model
from books.models import Genres, Comment
from django.contrib.auth.models import Permission
from django.test import Client


class GetPagesTestCase(TestCase):

    def check_correct_navbar(self, response):
        navbar_data = response.context_data['navbar']
        navbar_titles = ['Home', 'All books', 'My books', 'Add Book', 'Feedback']
        navbar_urls = ['home', 'books', 'user_books', 'add_book', 'feedback']

        self.assertEqual(len(navbar_data), 5)

        for item in navbar_data:
            self.assertIn(item['title'], navbar_titles)
            self.assertIn(item['url_name'], navbar_urls)


    def setUp(self):
        "init"


    def test_main_page(self):
        '''
        Check if the main page is displayed correctly when a request is made
        '''

        path = reverse('home')
        response = self.client.get(path)

        # check: get main page - status 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # check: get correct template
        self.assertTemplateUsed(response, 'books/index.html')

        # check: correct template in template_name
        self.assertIn('books/index.html', response.template_name)

        # check: correct title
        self.assertEqual(response.context_data['title'], 'Favourite Books')

        # check: correct navbar data
        self.check_correct_navbar(response)


    def test_redirect_addpage(self):
        '''
        Check Add Book page working correctly
        '''

        path = reverse('add_book')

        redirect_url = reverse('users:login') + '?next=' + path
        response = self.client.get(path)

        # check: redirect work correctly
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # check: redirect to correct page
        self.assertRedirects(response, redirect_url)


    def test_data_all_books(self):
        '''
        Check if the All Books page is displayed correctly when a request is made
        '''

        path = reverse('books')
        response = self.client.get(path)

        # check: get page - status 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # check: get correct template
        self.assertTemplateUsed(response, 'books/books.html')

        # check: correct template in template_name
        self.assertIn('books/books.html', response.template_name)

        # check: correct title
        self.assertEqual(response.context_data['title'], 'All Books')

        # check: correct navbar data
        self.check_correct_navbar(response)


    def tearDown(self):
        "clean"


class BooksFlowsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass', email='test@example.com')
        self.user2 = get_user_model().objects.create_user(username='otheruser', password='testpass2', email='other@example.com')
        self.genre = Genres.objects.create(genre='Fiction', slug='fiction')
        self.book = Book.objects.create(title='Book1', description='Desc', is_published=1, author=self.user, slug='book1')
        self.book.genres.add(self.genre)
        self.unpublished_book = Book.objects.create(title='Book2', description='Desc2', is_published=0, author=self.user, slug='book2')
        self.comment = Comment.objects.create(book=self.book, author=self.user, content='Nice book!')
        self.client = Client()

    def test_authenticated_book_creation(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('add_book'))
        self.assertEqual(response.status_code, 200)
        data = {
            'title': 'New Book',
            'description': 'Some desc',
            'is_published': 1,
            'genres': [self.genre.id],
        }
        response = self.client.post(reverse('add_book'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_book_creation_invalid(self):
        self.client.login(username='testuser', password='testpass')
        data = {'title': 'A'*101, 'description': 'desc', 'is_published': 1}
        response = self.client.post(reverse('add_book'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot exceed')

    def test_book_detail_view(self):
        response = self.client.get(reverse('book', kwargs={'book_slug': self.book.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)

    def test_unpublished_book_detail_permission(self):
        # Not author, should 404
        self.client.login(username='otheruser', password='testpass2')
        response = self.client.get(reverse('book', kwargs={'book_slug': self.unpublished_book.slug}))
        self.assertEqual(response.status_code, 404)
        # Author, should work
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('book', kwargs={'book_slug': self.unpublished_book.slug}))
        self.assertEqual(response.status_code, 200)

    def test_add_comment_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        data = {'content': 'Great!'}
        response = self.client.post(reverse('book', kwargs={'book_slug': self.book.slug}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='Great!').exists())


    def test_delete_comment_author(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_comment', kwargs={'comment_id': self.comment.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_non_author(self):
        self.comment = Comment.objects.create(book=self.book, author=self.user2, content='Other comment')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_comment', kwargs={'comment_id': self.comment.id}))
        self.assertNotEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_like_unlike_comment(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('like_comment', kwargs={'comment_id': self.comment.id})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user, self.comment.likes.all())
        # Unlike
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.comment.likes.all())

    def test_edit_book_author(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('edit_book', kwargs={'book_slug': self.book.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {'title': 'Edited Book', 'description': 'desc', 'is_published': 1, 'genres': [self.genre.id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Edited Book')

    def test_edit_book_non_author(self):
        self.client.login(username='otheruser', password='testpass2')
        url = reverse('edit_book', kwargs={'book_slug': self.book.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_book_author(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('delete_book', kwargs={'book_slug': self.book.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())

    def test_delete_book_non_author(self):
        self.client.login(username='otheruser', password='testpass2')
        url = reverse('delete_book', kwargs={'book_slug': self.book.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Book.objects.filter(id=self.book.id).exists())

    def test_feedback_form_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('feedback'))
        self.assertEqual(response.status_code, 200)

    def test_genre_filtering(self):
        response = self.client.get(reverse('tag', kwargs={'tag_slug': self.genre.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)

    def test_user_books_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)

    def test_permissions_add_book_requires_login(self):
        response = self.client.get(reverse('add_book'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('users:login'), response.url)
