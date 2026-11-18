**How to run the app on app1 / app2**
```bash
vagrant ssh app1
cd /opt/hall
sudo -u hall /opt/venv/bin/gunicorn -b 0.0.0.0:8000 --workers 2 --access-logfile - app:app
```
