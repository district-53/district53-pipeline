<<<<<<< HEAD
# district53-pipeline

# District53 Backend (Flask)

Backend service built with Python using the **Flask** microframework on **Ubuntu**.

---

## Setup & Installation

### 1. Clone the Repository
Download the project to your local machine and navigate to the root directory:
```bash
git clone <your-repository-url>
cd district53-project
```

### 2. Create and Activate a Virtual Environment
Create an isolated virtual environment named `.venv` and activate it:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Upgrade `pip` and install Flask all packages from `requirements.txt`:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the Server
Run the local Flask development server:
```bash
python app.py
```
or via the Flask CLI:
```bash
flask run
```

Once running, the application will be available at: **`http://127.0.0.1:5000`**

---

## Useful Development Commands

* **Save installed packages into `requirements.txt`:**
  ```bash
  pip freeze > requirements.txt
  ```
* **Deactivate the virtual environment:**
  ```bash
  deactivate
  ```
=======
**How to run the app on app1 / app2**
```bash
vagrant ssh app1
cd /opt/hall
sudo -u hall /opt/venv/bin/gunicorn -b 0.0.0.0:8000 --workers 2 --access-logfile - app:app
```
>>>>>>> origin/main
