# -*- coding:utf-8 -*-
import re

from app import db
from app.models import User, Permission
from flask import render_template, url_for, flash, redirect, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, UserRemoveForm


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        the_user = User.query.filter(User.email.ilike(login_form.email.data)).first()
        if the_user is not None and the_user.verify_password(login_form.password.data):
            login_user(the_user, login_form.remember_me.data)
            flash(u'登录成功!  欢迎您 %s!' % the_user.name, 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名无效或密码错误!', 'danger')
    return render_template("login.html", form=login_form, title=u"登入")


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(u'您已经成功登出!', 'info')
    return redirect(url_for('main.index'))


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if len(re.findall(string=form.email.data, pattern=current_app.config['REGISTRATION_EMAIL_PATTERN'])) <= 0:
            flash(u"注册失败！请使用组织邮箱进行注册", "danger")
            return render_template('register.html', form=form, title=u"新用户注册")
        the_user = User(email=form.email.data,
                        name=form.name.data,
                        password=form.password.data)
        db.session.add(the_user)
        db.session.commit()
        flash(u'注册成功! 欢迎您 %s!' % form.name.data, 'success')
        login_user(the_user)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('register.html', form=form, title=u"新用户注册")


@auth.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    form = ChangePasswordForm()
    user = db.session.query(User).filter(User.id == user_id).first()
    if form.validate_on_submit():
        if not current_user.can(Permission.UPDATE_OTHERS_INFORMATION) and \
                current_user.id != user.id:
            flash(u'密码更新失败!', 'error')
            return redirect(url_for('user.detail', user_id=user.id))
        user.password = form.new_password.data
        db.session.add(user)
        db.session.commit()
        flash(u'密码更新成功!', 'info')
        return redirect(url_for('user.detail', user_id=user.id))
    return render_template('user_edit.html', form=form, user=user, title=u"修改密码")


@auth.route('/remove_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def remove_user(user_id):
    form = UserRemoveForm()
    user = db.session.query(User).filter(User.id == user_id).first()
    if not form.validate_on_submit():
        return render_template('user_remove.html', form=form, user=user, title=u"删除用户")

    if not current_user.is_administrator():
        flash(u"您没有删除用户的权限!请联系管理员", "danger")
        return render_template('user_remove.html', form=form, user=user, title=u"删除用户")

    if user.email != form.email.data:
        flash(u"请输入正确的邮箱号码", "danger")
        return render_template('user_remove.html', form=form, user=user, title=u"删除用户")

    if user.email.lower() in [admin.lower() for admin in current_app.config['FLASKY_ADMIN']]:
        flash(u"禁止删除初始管理员账户!", "danger")
        return render_template('user_remove.html', form=form, user=user, title=u"删除用户")
    if user.have_borrowed_book():
        flash(u"该用户有书未归还，请待其归还后重试", "danger")
        return render_template('user_remove.html', form=form, user=user, title=u"删除用户")
    del_user = db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()
    flash(u"用户删除成功", "success")
    return redirect(url_for("user.index"))
