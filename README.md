# Tic-Tac-Toe Project

This project is a web-based Tic-Tac-Toe game with GPT-4 integration, built using Django for the backend and React for the frontend.

## Project Structure

- **`clarabackend/`**: Contains the Django backend code.
- **`clarafrontend/`**: Contains the React frontend code.
- **`venv/`**: Python virtual environment.
- **`db.sqlite3`**: SQLite database file.
- **`manage.py`**: Django management script.

## Prerequisites

- **Python 3.12** or later.
- **Node.js** and **npm** installed.

## FOR FIRST TIME SET UP ONLY

### 1. Create and Activate the Virtual Environment

Before running the project, create and activate the Python virtual environment:

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Backend Dependencies

With the virtual environment activated, install the necessary Python packages:

```bash
pip install -r requirements.txt
```

### 3. Apply Migrations

Make sure the database is up to date by applying any migrations:

```bash
python manage.py migrate
```

### 4. Start the Django Development Server

Start the Django backend server:

```bash
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000/`.

### 5. Navigate to the React Frontend Directory

Go to the React frontend directory:

```bash
cd clarafrontend
```

### 6. Install Frontend Dependencies

Install the necessary Node.js packages (only required the first time):

```bash
npm install
```

### 7. Start the React Development Server

Start the React frontend server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000/`.

## WHENEVER YOU COME BACK TO WORK ON THE PROJECT

1. **Activate the Virtual Environment:**

    **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

    **Windows:**
    ```bash
    venv\Scripts\activate
    ```

2. **Start the Django Server:**

    ```bash
    python manage.py runserver
    ```

3. **Start the React Server:**

    ```bash
    cd clarafrontend
    npm start
    ```

## Additional Notes

- **Stopping the Servers**: Press `CTRL+C` in the terminal where the servers are running to stop them.
- **Token Authentication**: The token returned from the `/auth/login/` endpoint is stored in `localStorage` for authentication.

## Troubleshooting

- If you encounter any issues with package installations, ensure that your virtual environment is active and you're in the correct directory before running commands.
- Check the browser's developer tools for any network or console errors during development.