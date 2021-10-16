import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from website import app, db, bcrypt
from website.forms import RegistrationForm, LoginForm, UpdateAccountForm, EmptyForm
from website.models import User
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/home")

def home():
    if current_user.is_authenticated:
        cur_usr_name = current_user.username
    else:
        cur_usr_name = "NONE"
    
    page = request.args.get('page', 1, type=int)
    #posts = Post.query.paginate(page = page, per_page = 1)
    users = User.query.paginate(page = page, per_page = 1)
    
    form = EmptyForm()
    return render_template('home.html', users=users, form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(page = page, per_page = 1)
    users = User.query.paginate(page = page, per_page = 1)
    form = EmptyForm()
    return render_template('home.html', users=users, posts=posts, form=form)

@app.route("/")
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/uploads/', picture_fn)

    output_size = (400, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    image_file = url_for('static', filename='uploads/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, user=current_user)






@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You should love yourself but you cant like yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You liked {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You should love yourself but you cant unlike yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You unliked {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route("/matched", methods=['GET'])
@login_required
def matched():
        #users = User.query.all()
        matches = current_user.followed_posts().all()
        return render_template('matched.html', title='Matched', matches = matches)

@app.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    form = EmptyForm()
    user = User.query.get_or_404(user_id)
    print(user_id)
    if user.id != current_user.id:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    form = EmptyForm()
    return redirect(url_for('login'))



