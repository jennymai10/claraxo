# Deploying the Tic-Tac-Toe Project on Google Cloud

## Prerequisites

### 1. Create a Google Cloud VM Instance

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **Compute Engine** > **VM Instances**.
3. Create a new VM instance with the following settings:
   - Select **Ubuntu 20.04** as the operating system.
   - Ensure firewall rules allow **HTTP** and **HTTPS** traffic.
4. Once the VM is running, SSH into the instance from the Google Cloud Console.

---

## Step 1: Install Required Software

### 1. **Update the System Packages**
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. **Install Python, Pip, and Virtualenv**
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. **Install Git**
```bash
sudo apt install git -y
```

---

## Step 2: Clone the Project Repository

### 1. **Generate a GitHub Access Token**
You'll need a GitHub personal access token to clone private repositories. [Follow this guide to generate a token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

### 2. **Clone the Repository**
```bash
git clone https://github.com/yourusername/your-repo.git
```
Replace `yourusername/your-repo` with the actual repository name. Use the GitHub token when prompted for a password.

---

## Step 3: Set Up the Backend (Django)

### 1. **Navigate to the Project Directory**
```bash
cd your-repo/tictactoe_project
```

### 2. **Create a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Set Up Environment Variables**
Create a `.env` file to store environment variables:
```bash
nano .env
```
Add the following content:
```bash
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=35.238.92.0  # Replace with your server's IP address
DATABASE_URL=sqlite:///db.sqlite3
```
Generate a `SECRET_KEY` using this command:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. **Run Database Migrations**
```bash
python3 manage.py migrate
```

### 6. **Collect Static Files**
```bash
python3 manage.py collectstatic
```

### 7. **Start the Backend using Gunicorn**
```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 tictactoe_backend.wsgi:application
```

---

## Step 4: Set Up the Frontend (React)

### 1. **Navigate to the Frontend Directory**
```bash
cd tictactoe_frontend/tic-tac-toe-frontend
```

### 2. **Install Node.js and NPM**
```bash
sudo apt install nodejs npm -y
```

### 3. **Install Frontend Dependencies**
```bash
npm install
```

### 4. **Set Up Frontend Environment Variables**
Create a `.env.production` file:
```bash
nano .env.production
```
Add the following:
```bash
REACT_APP_API_URL=https://35.238.92.0/api  # Replace with your backend API URL
REACT_APP_ENV=production
```

### 5. **Build the React App**
```bash
npm run build
```
The build folder will contain static files ready to be served.

---

## Step 5: Configure Nginx as a Reverse Proxy

### 1. **Install Nginx**
```bash
sudo apt install nginx -y
```

### 2. **Create an SSL Certificate**
To enable HTTPS, create a self-signed SSL certificate:
```bash
sudo mkdir /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt
```

### 3. **Configure Nginx**
Edit the Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/default
```
Replace the contents with the following configuration:
```nginx
server {
    listen 80;
    server_name 35.238.92.0;  # Replace with your IP address

    # Redirect all HTTP requests to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name 35.238.92.0;

    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;

    # Serve React frontend
    root /home/niijenn_0310/it_project_064/tictactoe_project/tictactoe_frontend/tic-tac-toe-frontend/build;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    # Proxy requests to Django backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. **Test Nginx Configuration**
```bash
sudo nginx -t
```
If there are no errors, restart Nginx:
```bash
sudo systemctl restart nginx
```

---

## Step 6: Run Gunicorn in the Background

### 1. **Create a Gunicorn Service File**
```bash
sudo nano /etc/systemd/system/gunicorn.service
```
Add the following configuration:
```ini
[Unit]
Description=gunicorn daemon for Django Tic Tac Toe
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/niijenn_0310/it_project_064/tictactoe_project
ExecStart=/home/niijenn_0310/it_project_064/tictactoe_project/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/niijenn_0310/it_project_064/tictactoe_project/gunicorn.sock \
          tictactoe_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. **Start and Enable Gunicorn**
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

## Step 7: Verify the Deployment

Visit your server's IP address in a browser:

- **Frontend**: `https://35.238.92.0/`
- **API Endpoints**: `https://35.238.92.0/api/login/` (or other API routes)

---

## Troubleshooting

- **Check Nginx Logs**:
  ```bash
  sudo tail -f /var/log/nginx/error.log
  ```

- **Check Gunicorn Logs**:
  ```bash
  sudo journalctl -u gunicorn
  ```