from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from .models import TicTacToeUser, Game

class TicTacToeTestCase(TestCase):
    def setUp(self):
        # This function runs before each test
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'Testpass123',
            'email': 'testuser@example.com',
            'profile_name': 'Test User',
            'age': 25
        }
        self.user = TicTacToeUser.objects.create_user(**self.user_data)

    def test_user_creation(self):
        # Ensure the user was created successfully
        user = TicTacToeUser.objects.get(username=self.user_data['username'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_signup_view(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'password2': 'Password123',
            'account_type': 1,
            'age': 21,
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful signup

    def test_email_verification(self):
        # Simulate sending a verification email
        mail.send_mail(
            'Email Verification',
            'Here is the verification code: 123456',
            'from@example.com',
            ['to@example.com'],
        )

        # Test if the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Email Verification', mail.outbox[0].subject)

    def test_login_view(self):
        # Ensure the login works with valid credentials
        login = self.client.post(reverse('login'), {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(login.status_code, 302)  # Should redirect after successful login