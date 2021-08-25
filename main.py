from app import create_app
import os

if __name__ == '__main__':
    port = os.environ.get("PORT")
    create_app().run(port=port, host='0.0.0.0')
