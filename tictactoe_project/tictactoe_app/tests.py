from django.test import TestCase, Client
from django.urls import reverse
from .models import TicTacToeUser, Game, GameLog
from django.contrib.auth import get_user_model
from django.core import mail
import json
from unittest.mock import patch

User = get_user_model()

class UserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'username': 'testuser',
            'password': 'Password123',
            'email': 'testuser@example.com',
            'account_type': 1,
            'profile_name': 'TestUser',
            'age': 25,
            'api_key': 'TestApiKey123',
        }
        cls.registration_url = reverse('register_user')
        cls.login_url = reverse('login_user')
        cls.verify_email_url = reverse('verify_email')

    def test_user_registration(self):
        """Test user registration form."""
        registration_data = self.user_data.copy()
        registration_data['password2'] = registration_data['password']  # Add password2 for form validation
        response = self.client.post(self.registration_url, registration_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)  # User should be inactive until email verification

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your verification code', mail.outbox[0].body)

    def test_email_verification(self):
        """Test user email verification."""
        user = User.objects.create_user(**self.user_data)
        user.verification_code = 123456
        user.is_active = False
        user.save()

        response = self.client.post(self.verify_email_url, {
            'username': 'testuser',
            'code': '123456',
        })
        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_invalid_email_verification(self):
        """Test invalid email verification."""
        user = User.objects.create_user(**self.user_data)
        user.verification_code = 123456
        user.is_active = False
        user.save()

        response = self.client.post(self.verify_email_url, {
            'username': 'testuser',
            'code': '999999',  # Incorrect numeric code
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid code or username')

    def test_login_user(self):
        """Test user login."""
        user = User.objects.create_user(
            username='testuser',
            password='Password123',
            email='testuser@example.com',
            account_type=1,
            profile_name='TestUser',
            age=25
        )
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    # @patch('django.core.mail.send_mail')
    # def test_email_sent(self, mock_send_mail):
    #     """Test that an email is sent during registration."""
    #     registration_data = self.user_data.copy()
    #     registration_data['password2'] = registration_data['password']  # Add password2 for form validation
    #
    #     response = self.client.post(self.registration_url, registration_data)
    #
    #     # Debugging: Check form errors if the status code is not as expected
    #     if response.status_code != 302:
    #         print("Form errors:", response.context['form'].errors)  # Print form errors for debugging
    #
    #     self.assertEqual(response.status_code, 302)  # Expect redirect after successful registration
    #     self.assertTrue(mock_send_mail.called)
    #     self.assertEqual(mock_send_mail.call_count, 1)


class TicTacToeGameTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='Password123',
            email='testuser@example.com',
            account_type=1,
            profile_name='TestUser',
            age=25
        )
        cls.user.is_active = True
        cls.user.save()

    def setUp(self):
        self.client.login(username='testuser', password='Password123')
        self.game_url = reverse('tictactoe_game')
        self.make_move_url = reverse('make_move')
        self.reset_game_url = reverse('reset_game')

    def assertBoardState(self, expected_board):
        """Helper to assert the board state."""
        session = self.client.session
        actual_board = session.get('board')
        self.assertEqual(actual_board, expected_board)

    def test_start_game(self):
        """Test game board initialization."""
        response = self.client.get(self.game_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Check that cell numbers are displayed

    def test_make_move(self):
        """Test making a move in the game."""
        session = self.client.session
        session['board'] = {
            '1': '', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        }
        session.save()

        # Player move
        response = self.client.post(self.make_move_url, json.dumps({'move': '1'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check AI move and board state
        game = Game.objects.get(player=self.user)
        self.assertEqual(GameLog.objects.filter(game=game).count(), 2)
        response_json = response.json()
        self.assertIn('ai_move', response_json)
        self.assertIn(response_json['ai_move'], ['2', '3', '4', '5', '6', '7', '8', '9'])

    def test_reset_game(self):
        """Test game reset functionality."""
        response = self.client.get(self.reset_game_url)
        self.assertEqual(response.status_code, 200)
        self.assertBoardState({
            '1': '', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        })

    def test_check_win(self):
        """Test the win condition check."""
        session = self.client.session
        session['board'] = {
            '1': 'X', '2': 'X', '3': 'X',  # X wins with a horizontal line
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        }
        session.save()

        # Check if X has already won
        response = self.client.post(self.make_move_url, json.dumps({'move': '4'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        game = Game.objects.get(player=self.user)
        self.assertEqual(game.winner, 'X')  # X should be the winner


    def test_draw_condition(self):
        """Test draw condition in Tic-Tac-Toe."""
        session = self.client.session
        session['board'] = {
            '1': 'X', '2': 'O', '3': 'X',
            '4': 'X', '5': 'O', '6': 'O',
            '7': 'O', '8': 'X', '9': ''
        }
        session.save()

        response = self.client.post(self.make_move_url, json.dumps({'move': '9'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        game = Game.objects.get(player=self.user)
        self.assertEqual(game.winner, 'Draw')

    def test_invalid_move(self):
        """Test attempting to make an invalid move (already occupied square)."""
        session = self.client.session
        session['board'] = {
            '1': 'X', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        }
        session.save()

        # Attempt to move to a square that's already occupied
        response = self.client.post(self.make_move_url, json.dumps({'move': '1'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Expecting bad request since the square is occupied
