from flask import make_response,render_template, session, redirect, url_for, current_app,abort,flash,request
from .. import db,photos
from ..models import Role,User,Permission,Post
from ..email import send_email
from . import main
from .forms import PostForm,NameForm,EditProfileForm,EditProfileAdminForm,UploadForm
from flask_login import login_user,login_required,logout_user
from flask_login import  current_user
from ..decorators import admin_required,permission_required
import os

# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             session['known'] = False
#             if current_app.config['FLASKY_ADMIN']:
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',
#                            form=form, name=session.get('name'),
#                            known=session.get('known', False))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been update.')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

@main.route('/edit-gravatar',methods=['GET','POST'])
@login_required
def edit_gravatar():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        current_user.gravatar = file_url
        db.session.add(current_user)
        flash('修改成功!')
        return redirect(url_for('.user',username=current_user.username,file_url=file_url))

    return render_template('edit_gravatar.html',form=form,file_url=current_user.gravatar)

#文章路由
@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    show_followed = False
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page',1,type=int)
    #分页
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination,show_followed=show_followed)

#文章固定链接
@main.route('/post/<int:id>')
def post(id):
    post =Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

#编辑界面
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('文章更新成功!')
        return redirect(url_for('post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('您未登录,无效操作.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('您已经关注了该用户~')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash('正在关注用户: %s.'%username)
    return redirect(url_for('.user',username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请登录后再试!')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title="的粉丝",
                           endpoint='.followers',pagination=pagination,
                           follows=follows)

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请登录后再试!')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('您本来就没有关注此用户.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('您将不再关注 %s .' % username)
    return redirect(url_for('.user', username=username))

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未登录用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="正在关注",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_all_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp