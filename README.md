
# Clara Tic Tac Toe Project

This project is a Django-based web application that includes a Tic Tac Toe game interface and a RESTful API using Django Rest Framework (DRF). It also integrates with GPT-4 API for AI-based gameplay.

## Prerequisites

Before setting up the project, ensure you have the following installed on your machine:

- Python 3.11 (other versions may work, but this is the recommended version)
- pip (Python package installer)
- Git (for version control)
- OPEN API KEY: Apparently, OpenAI still allow a free $5 credit for new account. Please go to Open AI, create an account.
  Then go to Dashboard => API keys => Create new secret key => Create secret key => THEN SAVE THE KEY SOMEWHERE, YOU CAN NEVER FIND IT AGAIN IF YOU LOSE IT.

## Project Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/clara-tictactoe.git
cd clara-tictactoe
```

### 2. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

This should install most of what you need. But later on, if it says anything like Can't find module abcxyz. Then simply do a pip install that module.

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory (the root folder is where your 'manage.py' located) to store your environment variables. Use the following template:

```env
DJANGO_DEBUG=True
OPENAI_API_KEY=your_openai_api_key_here
CLARA_ENVIRONMENT=local
CLARA=/full_path/to/root_folder_here
FILE_STORAGE_TYPE=local
DB_TYPE=sqlite
```

### 5. Apply Migrations

Apply the database migrations to set up your database schema:

```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional for now, you can skip)

To access the Django admin interface, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin user.

### 7. Running the Development Server

You need to start both the Q-cluster and the Django development server.

#### Terminal 1: Start the Q-cluster

```bash
python manage.py qcluster
```

#### Terminal 2 (A DIFFERENT TERMINAL): Start the Django Development Server

```bash
python manage.py runserver
```

### 8. Access the Application

Open your web browser and go to (bookmark these on browser for quick retrieval later on):

- The Tic Tac Toe interface: `http://localhost:8000/tictactoe/`
- The Django admin: `http://localhost:8000/admin/`

### 10. Frontend Development (Optional)

If you plan to develop the frontend separately, ensure you have Node.js and npm installed. Navigate to the `tictactoe_frontend` directory and run:

```bash
npm install
npm start
```

### 11. Committing Changes

Before committing changes to the repository, ensure the `.gitignore` file excludes unnecessary files, ESPECIALLY the .env file where you put your OPEN API key because we don't want your key to be on Git and people use your credits.

### 12. Deploying to Production (Skip for now)

For deployment, you will need to set environment variables in your production environment (e.g., using Heroku or another platform) and switch the `CLARA_ENVIRONMENT` to `heroku`.

## WORKING ON THE PROJECT:

When coding and contributing to the git repo, the repo has enabled branch protection rules.

You can only commit to your own branch (create one from `main`), and then create a pull request from your branch to `main`.

At least 1 code review is required to merge your code into `main`. Please reach out =))

### WHENEVER YOU COME BACK TO CODE, the folder `tictactoe_project` is the only folder you should care about or modify. All the others are belonged to the client's previous codebase and should not be modified.

Go into your virtual env:
```bash
source venv/bin/activate
alias python=python3
# On Windows use `venv\Scripts\activate`
```

If not already in `tictactoe_project` folder:
```bash
cd tictactoe_project
```

Update dependencies:
```bash
make install
# or if doesn't work then:
pip install -r requirements.txt
```

Apply the database migrations to set up your database schema:
```bash
make migrate
# or if doesn't work then:
python manage.py makemigrations
python manage.py migrate
```

Start both the Q-cluster and the Django development server.

Terminal 1: Start the Q-cluster

```bash
make qcluster
# or if doesn't work then:
python manage.py qcluster
```

Terminal 2 (A DIFFERENT TERMINAL): Start the Django Development Server

```bash
make run
# or if doesn't work then:
python manage.py runserver
```

Open your web browser and go to (bookmark these on the browser for quick retrieval later on):

- The Tic Tac Toe interface: `http://localhost:8000/`
- The Django admin: `http://localhost:8000/admin/`
