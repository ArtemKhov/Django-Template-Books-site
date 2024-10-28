from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from books.models import Book


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
