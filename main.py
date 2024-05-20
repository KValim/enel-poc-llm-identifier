"""
This script runs the Flask application.

It creates an instance of the Flask app using the `create_app` factory function
from the `app` module and runs the app in debug mode if the script is executed directly.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
