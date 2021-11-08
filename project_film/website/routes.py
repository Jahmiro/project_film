from flask import render_template, url_for, flash, redirect, request, abort
from website import app, db, bcrypt
from website.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    PostForm,
    ActeurForm,
    RegisseurForm
)
from website.models import User, Post, Acteur, Regisseur, Film, Rol
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            name=form.name.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Je account is aangemaakt!", "succes")
        return redirect(url_for("login"))

    return render_template("signup.html", title="Signup", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "error")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template("account.html", title="Account", form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Je opmerking is geplaatst", "success")
    return render_template(
        "create_post.html", title="New Post", form=form, legend="Reactie plaatsen"
    )


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title="Posts", post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Je reactie is geupdate", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update reactie"
    )


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Je reactie is verwijderd", "success")
    return redirect(url_for("new_post"))


@app.route("/user/<string:name>")
def user_posts(name):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(name=name).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.data_posted.desc())
        .paginate(page=page, per_page=100)
    )
    return render_template("user_posts.html", posts=posts, user=user)


@app.route("/acteur/new", methods=["GET", "POST"])
@login_required
def new_acteur():
    form = ActeurForm()
    if form.validate_on_submit():
        acteur = Acteur(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            title=form.title.data,
            name_character=form.rol.data
        )
        rol = Rol(
            title=form.title.data,
            name_character=form.rol.data
        )
        db.session.add(acteur)
        db.session.add(rol)
        db.session.commit()
        flash("Acteur is toegevoegd", "success")
    return render_template(
        "create_acteur.html", title="New acteur", form=form, legend="Acteur toevoegen"
    )

@app.route("/acteur/<int:acteur_id>")
def acteur(acteur_id):
    acteur = Acteur.query.get_or_404(acteur_id)
    return render_template("acteur.html", title="Acteurs", acteur=acteur)

@app.route("/acteur/<int:acteur_id>/update", methods=["GET", "POST"])
@login_required
def update_acteur(acteur_id):
    acteur = Acteur.query.get_or_404(acteur_id)
    form = ActeurForm()
    if form.validate_on_submit():
        acteur.title = form.title.data
        acteur.first_name = form.first_name.data
        acteur.last_name = form.last_name.data
        acteur.name_character = form.rol.data
        db.session.commit()
        flash("Acteur is geupdate", "success")
        return redirect(url_for("acteur", acteur_id=acteur.id))
    elif request.method == "GET":
        form.title.data = acteur.title
        form.first_name.data = acteur.first_name
        form.last_name.data = acteur.last_name
        form.rol.data = acteur.name_character 
    return render_template(
        "create_acteur.html", title="Update acteur", form=form, legend="Update acteur"
    )


@app.route("/acteur/<int:acteur_id>/delete", methods=["POST"])
@login_required
def delete_acteur(acteur_id):
    acteur = Acteur.query.get_or_404(acteur_id)
    db.session.delete(acteur)
    db.session.commit()
    flash("Acteur is verwijderd", "success")
    return redirect(url_for("new_acteur"))

@app.route("/regisseur/new", methods=["GET", "POST"])
@login_required
def new_regisseur():
    form = RegisseurForm()
    if form.validate_on_submit():
        regisseur = Regisseur(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            title=form.title.data,
        )

        db.session.add(regisseur)
        db.session.commit()
        flash("Regisseur is toegevoegd", "success")
    return render_template(
        "create_regisseur.html", title="New regisseur", form=form, legend="Regisseur toevoegen"
    )

@app.route("/regisseur/<int:regisseur_id>")
def regisseur(regisseur_id):
    regisseur = Regisseur.query.get_or_404(regisseur_id)
    return render_template("regisseur.html", title="Regisseurs", regisseur=regisseur)

@app.route("/regisseur/<int:regisseur_id>/update", methods=["GET", "POST"])
@login_required
def update_regisseur(regisseur_id):
    regisseur = Regisseur.query.get_or_404(regisseur_id)
    form = RegisseurForm()
    if form.validate_on_submit():
        regisseur.title = form.title.data
        regisseur.first_name = form.first_name.data
        regisseur.last_name = form.last_name.data
        regisseur.name_character = form.last_name_character.data
        db.session.commit()
        flash("Regisseur is geupdate", "success")
        return redirect(url_for("regisseur", regisseur_id=regisseur.id))
    elif request.method == "GET":
        form.title.data = regisseur.title
        form.first_name.data = regisseur.first_name
        form.last_name.data = regisseur.last_name
    return render_template(
        "create_regisseur.html", title="Update regisseur", form=form, legend="Update regisseur"
    )

@app.route("/regisseur/<int:regisseur_id>/delete", methods=["POST"])
@login_required
def delete_regisseur(regisseur_id):
    regisseur = Regisseur.query.get_or_404(regisseur_id)
    db.session.delete(regisseur)
    db.session.commit()
    flash("Regisseur is verwijderd", "success")
    return redirect(url_for("new_regisseur"))

@app.route("/films", methods=["GET", "POST"])
def films():
    return render_template("films.html", title="Films")


@app.route("/black-panther", methods=["GET", "POST"])
def film1():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film1.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)


@app.route("/guardians-of-the-galaxy", methods=["GET", "POST"])
def film2():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film2.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)


@app.route("/infinity-war", methods=["GET", "POST"])
def film3():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film3.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)


@app.route("/thor-ragnarok", methods=["GET", "POST"])
def film4():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film4.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)


@app.route("/captain-america-civil-war", methods=["GET", "POST"])
def film5():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film5.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)


@app.route("/ant-man-and-the-wasp", methods=["GET", "POST"])
def film6():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.data_posted.desc()).paginate(
        page=page, per_page=100
    )
    acteurs = Acteur.query.paginate(
        page=page, per_page=100
    )
    regisseurs = Regisseur.query.paginate(
    page=page, per_page=100
    )
    return render_template("film-paginas/film6.html", title="Films", posts=posts, acteurs=acteurs, regisseurs=regisseurs)
