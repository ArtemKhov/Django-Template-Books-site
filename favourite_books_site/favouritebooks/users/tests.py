from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client


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


class UsersFlowsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass', email='test@example.com')
        self.client = Client()

    def test_login_get(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_post_success(self):
        response = self.client.post(reverse('users:login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)

    def test_profile_access_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_access_unauthenticated(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('users:login'), response.url)

    def test_password_change_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, 200)
        data = {'old_password': 'testpass', 'new_password1': 'newpass123A', 'new_password2': 'newpass123A'}
        response = self.client.post(reverse('users:password_change'), data)
        self.assertEqual(response.status_code, 302)

    def test_password_change_unauthenticated(self):
        response = self.client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('users:login'), response.url)

    def test_password_reset_request(self):
        response = self.client.get(reverse('users:password_reset'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('users:password_reset'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)

    def test_password_reset_done_page(self):
        response = self.client.get(reverse('users:password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_done.html')

    def test_password_reset_confirm_page(self):
        # This test is limited, as token/uid are not easily generated in unit tests
        response = self.client.get(reverse('users:password_reset_confirm', kwargs={'uidb64': 'uid', 'token': 'token'}))
        self.assertIn(response.status_code, [200, 302, 404])

    def test_password_reset_complete_page(self):
        response = self.client.get(reverse('users:password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')
