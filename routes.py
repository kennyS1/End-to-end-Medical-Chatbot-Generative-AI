from flask import render_template, request, redirect, url_for, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Todo
from werkzeug.security import generate_password_hash, check_password_hash
import os

def init_routes(app):

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('用户名已存在', 'error')
                return redirect(url_for('register'))
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                access_token = create_access_token(identity={'user_id': user.id})
                return redirect(url_for('todos'))
            flash('用户名或密码错误', 'error')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/todos', methods=['GET', 'POST'])
    @login_required
    def todos():
        if request.method == 'POST':
            title = request.form['title']
            new_todo = Todo(title=title, user_id=current_user.id)
            db.session.add(new_todo)
            db.session.commit()
            flash('Todo 添加成功', 'success')
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return render_template('todos.html', todos=todos)

    @app.route('/todo/delete/<int:todo_id>', methods=['POST'])
    @login_required
    def delete_todo(todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if todo.user_id != current_user.id:
            flash('无权限删除', 'error')
            return redirect(url_for('todos'))
        db.session.delete(todo)
        db.session.commit()
        flash('Todo 删除成功', 'success')
        return redirect(url_for('todos'))

    @app.route('/todo/toggle/<int:todo_id>', methods=['POST'])
    @login_required
    def toggle_todo(todo_id):
        todo = Todo.query.get_or_404(todo_id)
        if todo.user_id != current_user.id:
            flash('无权限修改', 'error')
            return redirect(url_for('todos'))
        todo.completed = not todo.completed
        db.session.commit()
        flash('Todo 状态更新成功', 'success')
        return redirect(url_for('todos'))