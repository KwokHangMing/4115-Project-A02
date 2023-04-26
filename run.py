
from app import app
import subprocess

subprocess.run(["flask","db","upgrade"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
