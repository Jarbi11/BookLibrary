# -*- coding:utf-8 -*-
from flask import render_template, url_for, flash, redirect, request, abort, g, current_app
from flask_login import login_required, current_user
from app.models import User, Log, Permission, Role
from .forms import EditProfileForm, AvatarEditForm, AvatarUploadForm, RoleChangeForm
from ..decorators import admin_required, permission_required
from app import db, avatars
from . import user
import json


@user.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page=10)
    users = pagination.items
    return render_template("user.html", users=users, pagination=pagination, title=u"已注册用户")


@user.route('/<int:user_id>/')
def detail(user_id):
    the_user = User.query.get_or_404(user_id)

    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = the_user.logs.filter_by(returned=show) \
        .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=5)
    logs = pagination.items

    return render_template("user_detail.html", user=the_user, logs=logs, pagination=pagination,
                           title=u"用户: " + the_user.name)


@user.route('/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    if current_user.id == user_id or current_user.can(Permission.UPDATE_OTHERS_INFORMATION):
        the_user = User.query.get_or_404(user_id)
        form = EditProfileForm()
        if form.validate_on_submit():
            the_user.name = form.name.data
            # the_user.major = form.major.data
            the_user.headline = form.headline.data
            the_user.about_me = form.about_me.data
            db.session.add(the_user)
            db.session.commit()
            flash(u'资料更新成功!', "info")
            return redirect(url_for('user.detail', user_id=user_id))
        form.name.data = the_user.name
        # form.major.data = the_user.major
        form.headline.data = the_user.headline
        form.about_me.data = the_user.about_me

        return render_template('user_edit.html', form=form, user=the_user, title=u"编辑资料")
    else:
        abort(403)


@user.route('/<int:user_id>/avatar_edit/', methods=['GET', 'POST'])
@login_required
def avatar(user_id):
    if current_user.id == user_id or current_user.can(Permission.UPDATE_OTHERS_INFORMATION):
        the_user = User.query.get_or_404(user_id)
        avatar_edit_form = AvatarEditForm()
        avatar_upload_form = AvatarUploadForm()
        if avatar_upload_form.validate_on_submit():
            if 'avatar' in request.files:
                forder = str(user_id)
                avatar_name = avatars.save(avatar_upload_form.avatar.data, folder=forder)
                the_user.avatar = json.dumps({"use_out_url": False, "url": avatar_name})
                db.session.add(the_user)
                db.session.commit()
                flash(u'头像更新成功!', 'success')
                return redirect(url_for('user.detail', user_id=user_id))
        if avatar_edit_form.validate_on_submit():
            the_user.avatar = json.dumps({"use_out_url": True, "url": avatar_edit_form.avatar_url.data})
            db.session.add(the_user)
            db.session.commit()
            return redirect(url_for('user.detail', user_id=user_id))
        return render_template('avatar_edit.html', user=the_user, avatar_edit_form=avatar_edit_form,
                               avatar_upload_form=avatar_upload_form, title=u"更换头像")
    else:
        abort(403)


@user.route('/<int:user_id>/role_change/', methods=['GET', 'POST'])
@login_required
def change_role(user_id):
    if not current_user.can(Permission.UPDATE_OTHERS_INFORMATION):
        abort(403)
    else:
        the_user = User.query.get_or_404(user_id)
        role_change_form = RoleChangeForm()
        if role_change_form.validate_on_submit():
            the_user.role = Role.query.filter(Role.name == role_change_form.role.data).first()
            the_user.role_id = the_user.role.id
            if the_user.email.lower() in [admin.lower() for admin in current_app.config['FLASKY_ADMIN']]:
                flash(u"禁止修改初始管理员权限!")
                return redirect(url_for("user.detail", user_id=user_id))
            db.session.add(the_user)
            db.session.commit()
            flash(u"用户权限更新成功！", "success")
            return redirect(url_for("user.detail", user_id=user_id))
        return render_template('role_change.html', user=the_user, role_change_form=role_change_form,
                               title=u"更改用户权限")
