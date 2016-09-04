# -*- coding: utf-8 -*-
from . import admin
from .forms import LoginForm
from ..models import User
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user  # 保护路由只让认证用户登陆, 保存登陆用户


@admin.route('/')
@login_required
def index():

    return render_template('base/layout.html')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=True)  # True，在cookie中写入长期有效的cookie
            return redirect(request.args.get('next') or url_for('admin.index'))  # 后台默认页
        flash('Invalid username or password.')
    return render_template('admin/login.html', form=form)


@login_required
@admin.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
