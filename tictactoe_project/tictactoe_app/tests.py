# from django.test import TestCase, Client
# from django.urls import reverse
# from django.core import mail
# from .models import TicTacToeUser

# class UserRegistrationTests(TestCase):
#     """
#     Test case for user registration functionality in the TicTacToe application.
    
#     This class contains tests to validate that:
#     - A user can successfully submit a valid registration form.
#     - The user receives an email with a verification code.
#     - User data is correctly saved in the database after registration.
#     """

#     def setUp(self):
#         """
#         Set up the test client and relevant URLs for registration, email verification, login, and users.

#         The test client simulates HTTP requests to the Django application, and the reverse function
#         retrieves the URLs for the respective views by name.
#         """
#         self.client = Client()  # Simulates a browser
#         self.register_url = reverse('register_user')  # URL for registration view
#         self.verify_email_url = reverse('verify_email')  # URL for email verification view
#         self.login_url = reverse('login_user')  # URL for login view
#         self.users_url = reverse('get_users')  # URL for the users view

#     def test_registration_form_valid_submission(self):
#         """
#         Test the registration flow with valid form data.

#         This test ensures that when valid form data is submitted:
#         - The user is created successfully.
#         - The user is inactive (as the email needs to be verified).
#         - A verification code is generated and sent via email.
#         - The server responds with a redirect (status code 302) after successful submission.
#         """
#         # Simulate a POST request with valid form data for registration
#         response = self.client.post(self.register_url, {
#             'username': 'testuser',
#             'password': 'securepassword123',  # Must match the app's password rules
#             'email': 'test@example.com',
#             'account_type': 1,  # Assuming 1 = Player
#             'profile_name': 'Test User',
#             'age': 25,
#             'api_key': 'sampleapikey123'
#         })
#         # Check if the response status code is 302 (redirect after successful form submission)
#         self.assertEqual(response.status_code, 302)
        
#         # Check if the user was created in the database
#         user = TicTacToeUser.objects.get(username='testuser')
#         # Verify that the user is inactive, as they must verify their email first
#         self.assertFalse(user.is_active)
#         # Check that a verification code was generated for the user
#         self.assertIsNotNone(user.verification_code)

#         # Check if an email was sent (Django stores sent emails in a test outbox)
#         self.assertEqual(len(mail.outbox), 1)
#         # Verify that the email body contains the correct verification code
#         self.assertIn(str(user.verification_code), mail.outbox[0].body)

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
        """
        Set up test data for the UserTests class.

        This method is run once for the entire class. It initializes user registration data
        and stores the URLs for user registration, login, and email verification endpoints.

        Attributes:
            cls.user_data (dict): Default user registration data including username, password, email, etc.
            cls.registration_url (str): URL for user registration.
            cls.login_url (str): URL for user login.
            cls.verify_email_url (str): URL for verifying user email.
        """

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
        """
        Test user registration functionality.

        This test ensures that a new user can register successfully with valid data.
        It checks that:
            - The user registration is successful and returns a status code of 302.
            - The user is created and exists in the database.
            - The user is initially inactive until email verification.
            - A verification email is sent to the user's email address.
        """
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
        """
        Test the user email verification process.

        This test creates an inactive user with a verification code and simulates an email
        verification request. It checks that:
            - The verification process completes successfully and returns a status code of 302.
            - The user's account is activated after successful verification.
        """
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
        """
        Test invalid email verification attempts.

        This test creates an inactive user with a verification code and then attempts
        to verify using an incorrect code. It checks that:
            - The server returns a status code of 200 indicating an invalid attempt.
            - The user account remains inactive.
            - An appropriate error message is returned.
        """
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
        """
        Test the user login process.

        This test creates and activates a user, then simulates a login request.
        It checks that:
            - The login request completes successfully and returns a status code of 302.
            - The user is authenticated and the session contains the correct user ID.
        """
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
        """
        Set up test data for the TicTacToeGameTests class.

        This method is run once for the entire class. It creates an active test user
        for the game-related tests.

        Attributes:
            cls.user (User): A test user who is created and activated.
        """
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
        """
        Set up the initial state for each test in TicTacToeGameTests.

        This method is run before each test. It logs in the test user and initializes
        URLs for game-related actions.

        Attributes:
            self.game_url (str): URL for starting a new Tic-Tac-Toe game.
            self.make_move_url (str): URL for making a move in the Tic-Tac-Toe game.
            self.reset_game_url (str): URL for resetting the game board.
        """
        self.client.login(username='testuser', password='Password123')
        self.game_url = reverse('tictactoe_game')
        self.make_move_url = reverse('make_move')
        self.reset_game_url = reverse('reset_game')

    def assertBoardState(self, expected_board):
        """
        Helper method to assert the current state of the game board.

        This method checks that the current game board state in the session matches
        the expected board state.

        Args:
            expected_board (dict): A dictionary representing the expected state of the game board.
        """
        session = self.client.session
        actual_board = session.get('board')
        self.assertEqual(actual_board, expected_board)

    def test_start_game(self):
        """
        Test initializing a new game.

        This test checks that:
            - A new game can be started successfully.
            - The response status code is 200.
            - The response contains the initial cell numbers indicating the game board is displayed.
        """
        response = self.client.get(self.game_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Check that cell numbers are displayed

    def test_make_move(self):
        """
        Test making a move in the Tic-Tac-Toe game.

        This test sets up an empty game board and simulates a player making a move.
        It checks that:
            - The move is processed successfully with a status code of 200.
            - The AI (computer) also makes a move.
            - The game log is updated with both player and AI moves.
            - The AI's move is a valid and available cell on the board.
        """
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
        """
        Test resetting the game board.

        This test checks that:
            - The game board is reset to its initial empty state.
            - The response status code is 200.
            - The board state matches an empty game board.
        """
        response = self.client.get(self.reset_game_url)
        self.assertEqual(response.status_code, 200)
        self.assertBoardState({
            '1': '', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        })

    def test_check_win(self):
        """
        Test the win condition check in the Tic-Tac-Toe game.

        This test sets up the game board with a winning state for player 'X' (three 'X' marks in a row).
        It then attempts to make an additional move and checks that:
            - The response status code is 200, indicating the move was processed successfully.
            - The game correctly records 'X' as the winner.

        Board State Before Move:
            1: 'X', 2: 'X', 3: 'X',
            4: '',  5: '',  6: '',
            7: '',  8: '',  9: ''

        Winning Condition:
            'X' wins with a horizontal line on the top row (1, 2, 3).
        """
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
        """
        Test the draw condition in the Tic-Tac-Toe game.

        This test sets up the game board in a near-draw state with one move remaining.
        It then makes the final move, resulting in a draw, and checks that:
            - The response status code is 200, indicating the move was processed successfully.
            - The game correctly records the result as a draw.

        Board State Before Move:
            1: 'X', 2: 'O', 3: 'X',
            4: 'X', 5: 'O', 6: 'O',
            7: 'O', 8: 'X', 9: ''

        Final Move:
            Player 'X' moves to position 9, resulting in no available winning moves.
        """
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
        """
        Test making an invalid move in the Tic-Tac-Toe game.

        This test sets up the game board with the first cell already occupied by 'X'.
        It then attempts to make a move to the same cell and checks that:
            - The response status code is 400, indicating a bad request due to an invalid move.
            - The server returns an error message, as the cell is already occupied.

        Board State Before Move:
            1: 'X', 2: '',  3: '',
            4: '',  5: '',  6: '',
            7: '',  8: '',  9: ''

        Invalid Move:
            Player attempts to move to position 1, which is already occupied.
        """
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