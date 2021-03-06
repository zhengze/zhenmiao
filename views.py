# -*- coding: utf-8 -*-

import sqlite3
from flask import render_template, abort, redirect, url_for, make_response, \
    g, request, session, flash
from contextlib import closing
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from forms import LoginForm, EntryForm
from init import app, config_name
from models import User, Entries

#def init_db():
#    with closing(connect_db()) as db:
#        with app.open_resource('schema.sql', mode='r') as f:
#            db.cursor().executescript(f.read())
#        db.commit()

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def page_not_found(error):
    #return render_template('page_not_found.html'), 404
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.route('/')
def show_entries():
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    entries = Entries.query.all()
    entries_count = Entries.query.count()
    form = EntryForm()
    return render_template('show_entries.html', entries=entries, form=form, entries_count=entries_count)

@app.route('/add', methods=['POST'])
@login_required
def add_entry():
    #if not g.user.is_authenticated():
    #    abort(401)
    if config_name == 'testing':
        g.db.execute('insert into entries (title, text) values (?, ?)',
                [request.form['title'], request.form['text']])
    else:
        g.db.execute('insert into entries (title, text) values (%s, %s)',
        [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            g.user = current_user
            user = User.query.filter_by(username=username, password=password).first()
            login_user(user)
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    else:
        form = LoginForm()
        
    return render_template('login.html', error=error, form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))

