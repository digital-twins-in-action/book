import awsgi
from digital_twin_api import app as flask_app

# The Flask application object is imported as 'flask_app' from app.py.


def handle(event, context):
    """
    This is the entry point for AWS Lambda.
    It uses aws_wsgi to wrap the Flask app for Lambda.
    """
    return awsgi.response(flask_app, event, context)
