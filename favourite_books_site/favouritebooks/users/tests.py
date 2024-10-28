from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegisterUserTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': 'user_test',
            'email': 'usertest@mail.ru',
            'password1': '12345678Aa',
            'password2': '12345678Aa',
        }


    def test_form_registration_get(self):
        '''
        Check if the registration form is displayed correctly when a request is made
        '''

        path = reverse('users:register')
        response = self.client.get(path)

        # check: get page - status 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # check: get correct template
        self.assertTemplateUsed(response, 'users/register.html')


    def test_user_registration_success(self):
        '''
        Checking the correctness of user registration
        '''

        user_model = get_user_model()
        path = reverse('users:register')
        response = self.client.post(path, self.data)

        # check: redirect after success registration
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # check: redirect to register-success page
        self.assertRedirects(response, reverse('users:register_success'))

        # check: new user add to DB
        self.assertTrue(user_model.objects.filter(username=self.data['username']).exists())


    def test_user_registration_password_error(self):
        '''
        Checking that the correct error appears when the wrong password is entered during registration.
        '''

        self.data['password2'] = '12345678A'
        path = reverse('users:register')
        response = self.client.post(path, self.data)

        # check: code 200 even if put incorrect data
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # check: valid error message
        self.assertContains(response, "The two password fields didn’t match.", html=True)


    def test_user_registration_user_exists_error(self):
        '''
        Checking that users with the same login cannot be registered.
        '''

        user_model = get_user_model()
        user_model.objects.create(username=self.data['username'])

        path = reverse('users:register')
        response = self.client.post(path, self.data)

        # check: code 200 even if put incorrect data
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # check: user already exists error message
        self.assertContains(response, "A user with that username already exists.")


    def tearDown(self):
        "clean"
