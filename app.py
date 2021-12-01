#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import string
import webbrowser

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


DEBUG = True
PORT = 5000


dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.secret_key = 'admin'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + dir_path.replace("\\", "/") + "/todo.db"

db = SQLAlchemy(app)


class Todo(db.Model):
    """
    Veri tabanında saklanacak verilerin modelini tanımlayan sınıf...
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)
    complete = db.Column(db.Boolean)
    date = db.Column(db.DateTime, nullable=False)
    finished_date = db.Column(db.DateTime, nullable=True)


@app.route("/")
def home():
    """
    Bu fonksiyon ana sayfa rotası için home.html'i yükler ve
    veri tabanından tüm verileri çekip gönderir.
    """

    title = 'Hızlı ve Kolay Yapılacaklar Listesi'
    todos = Todo.query.all()

    return render_template("home.html", todos=todos, title=title)


@app.route("/add", methods=["GET", "POST"])
def add_todo():
    """
    Bu rota, yeni bir todo ekler. Eğer form POST olarak gelmiş ise işlemleri yapıp
    ana sayfayı yükler. Eğer değil ise hiçbir işlem yapmadan ana sayfaya döner.
    """

    if request.method == "POST":
        title = string.capwords(request.form.get("todo_name").capitalize())
        content = request.form.get("todo_content")
        content = content[0].upper() + content[1:]
        now = datetime.now()
        new_todo = Todo(title=title, content=content, complete=False, date=now, finished_date=None)

        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route("/complete/<string:id>")
def complete_todo(id):
    """
    Bir todo'yu tamamlandı işareti koyar.
    """

    todo = Todo.query.filter_by(id=id).first()

    if todo == None:
        return redirect(url_for("home"))
    else:
        if todo.complete == False:
            todo.complete = True
            todo.finished_date = datetime.now()
        else:
            todo.complete = False
            todo.finished_date = None

        db.session.commit()

        return redirect(url_for("home"))


@app.route("/delete/<string:id>")
def delete_todo(id):
    """
    Seçilen bir todo'yu veri tabanından siler.
    """

    todo = Todo.query.filter_by(id=id).first()

    if todo == None:
        return redirect(url_for("home"))
    else:
        db.session.delete(todo)
        db.session.commit()

        return redirect(url_for("home"))


@app.route("/delete/all")
def delete_all_todos():
    """
    Eğer toplamda 10 veya daha fazla todo varsa yeni bir tuş eklenir.
    Ve bu tuş, basıldığında bir soru sorar: Bütün todo'lar silinecek, emin misiniz?
    """

    title = "Tüm Todo'ları Sil"
    todos = Todo.query.all()

    if todos == []:
        return redirect(url_for("home"))

    return render_template("delete_all_todos.html", todos=todos, title=title)


@app.route("/delete/all/sure")
def delete_all_todos_sure():
    """
    Eğer kullanıcı tüm todo'ları silmekte emin ise hepsini siler.
    """

    todos = Todo.query.all()

    for x in range(len(todos) - 1, -1, -1):
        db.session.delete(todos[x])

    db.session.commit()

    return redirect(url_for("home"))


@app.route("/detail/<string:id>")
def detail_todo(id):
    """
    Seçilmiş olan todo'nun detaylı bilgi sayfasını yükler.
    Todo yok ise ana sayfaya yönlendirilir.
    """

    todo = Todo.query.filter_by(id=id).first()

    if todo == None:
        return redirect(url_for("home"))
    else:
        return render_template("detail.html", todo=todo, title=todo.title)


@app.route("/edit/<string:id>")
def edit_todo(id):
    """
    Seçilmiş olan todo'nun düzenlenme sayfasını yükler.
    Todo yok ise ana sayfaya yönlendirilir.
    """

    todo = Todo.query.filter_by(id=id).first()

    if todo == None:
        return redirect(url_for("home"))
    else:
        return render_template("edit.html", todo=todo, title=todo.title)


@app.route("/change/<string:id>", methods=["GET", "POST"])
def change_todo(id):
    """
    Seçilmiş olan todo'nun düzenlenme sayfasını yükler.
    Todo yok ise ana sayfaya yönlendirilir.
    """

    todo = Todo.query.filter_by(id=id).first()

    if todo == None:
        return redirect(url_for("home"))
    else:
        new_title = request.form.get("new_todo_name").capitalize()
        new_content = request.form.get("new_todo_content")
        new_content = new_content[0].upper() + new_content[1:]
        keep_current_date = request.form.get("keep_date")

        todo.title = new_title
        todo.content = new_content

        if keep_current_date != True:
            todo.date = datetime.now()

        db.session.commit()

        return redirect(url_for("home"))


@app.errorhandler(404)
def todo_not_found(e):
    """
    Bulunamayan bir sayfa olursa 404.html'i yükler.
    """

    return render_template("404.html")


# Sunucuyu başlat!
if __name__ == "__main__":
	if not DEBUG:
		webbrowser.open_new(f'http://localhost:{PORT}')
	app.run(debug=DEBUG, port=PORT)
