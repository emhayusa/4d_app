from .config import url_login, url_api
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('registration', __name__)

@bp.route('/')
@bp.route('/register')
def register():
    return render_template('registration/register.html', url_login=url_login, url_api=url_api)

#@bp.route('/login')
#def login():
#    return render_template('registration/login.html')

@bp.route('/activate/<token>')
def activate(token):
    return render_template('registration/activate.html', token=token, url_api=url_api, url_login=url_login)

@bp.route('/forgot')
def forgot():
    return render_template('registration/forgot.html', url_login=url_login, url_api=url_api)

@bp.route('/password/<token>')
def password(token):
    return render_template('registration/password.html', token=token, url_login=url_login, url_api=url_api)
