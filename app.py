from flask import Flask, render_template, request, redirect, url_for, session, abort


# main entry point for application, loads packages as blueprints to provide functionality
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
app.config['UPLOAD_IMAGE_PATH'] = 'static/submissions/images'
# set secret key
from settings import settings
app.secret_key=settings.SECRETS["FLASK_KEY"]


# import helios module
from libhelios import helios
app.register_blueprint(helios)
# import artemis module
from artemis import artemis
app.register_blueprint(artemis)


if __name__ == '__main__':
    app.run(debug=True,ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port=443)


