from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'database.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY,
            count INTEGER
        )''')
        conn.execute("INSERT OR IGNORE INTO visits (id, count) VALUES (1, 0)")

@app.before_request
def track_visits():
    if request.endpoint != 'static':
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE visits SET count = count + 1 WHERE id = 1")

@app.route('/')
def index():
    with sqlite3.connect(DB_PATH) as conn:
        posts = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    with sqlite3.connect(DB_PATH) as conn:
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return render_template('post.html', post=post)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' in session:
        with sqlite3.connect(DB_PATH) as conn:
            posts = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
            visits = conn.execute("SELECT count FROM visits WHERE id = 1").fetchone()[0]
        return render_template('admin.html', posts=posts, visits=visits)

    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin'))

@app.route('/add', methods=['POST'])
def add():
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    title = request.form['title']
    content = request.form['content']
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)", (title, content, datetime.now()))
    return redirect(url_for('admin'))

@app.route('/delete/<int:post_id>')
def delete(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    return redirect(url_for('admin'))

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    with sqlite3.connect(DB_PATH) as conn:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            conn.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?", (title, content, post_id))
            return redirect(url_for('admin'))
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return render_template('edit.html', post=post)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)