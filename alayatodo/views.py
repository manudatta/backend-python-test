from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify
    )
from flask_paginate import (
    Pagination,
    get_page_parameter 
)

from alayatodo.models import (
    User,
    Todo,
    db_session,
    obj2dict)

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    kwargs = {'username':username,'password':password}
    user = User.query.filter_by(**kwargs).first()
    if user:
        session['user'] = obj2dict(user)
        session['logged_in'] = True
        return redirect('/todo')
    return redirect('/login')


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')




@app.route('/todo/<int:id>', methods=['GET'])
@app.route('/todo/<int:id>/<string:content_type>', methods=['GET'])
@login_required
def todo(id,content_type='html'):
    user_id = session['user']['id']
    kwargs = {'user_id':user_id,'id':id}
    todo = Todo.query.filter_by(**kwargs).first()
    if content_type == 'json':
        return jsonify(obj2dict(todo))
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    user_id = session['user']['id']
    todos = Todo.query.filter_by(user_id=user_id).all()
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page-1)*per_page
    todos_render = todos[offset:(offset+per_page)]
    pagination = Pagination(page=page,per_page=per_page,offset=offset
                            ,bs_version=3, total=len(todos)
                            ,search=search,record_name='todos')
    return render_template('todos.html', todos=todos_render,pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    desc =  request.form.get('description', '')
    if len(desc) > 0:
        user_id = session['user']['id']
        todo_item = Todo(user_id=user_id,description=desc)
        db_session.add(todo_item)
        db_session.commit()
        flash(u'Todo item successfully created','success')
    else:
        flash(u'Todo item not created. Description is requireid.','error')
    return redirect('/todo')


@app.route('/todo/<int:id>', methods=['POST'])
@login_required
def todo_delete(id):
    user_id = session['user']['id']
    kwargs = {'user_id':user_id,'id':id}
    Todo.query.filter_by(**kwargs).delete()
    db_session.commit()
    flash(u'Todo successfully deleted','success')
    return redirect('/todo')


@app.route('/todo/<int:id>', methods=['PATCH'])
@login_required
def todos_patch(id):
    user_id = session['user']['id']
    done = request.form.get("done",None)
    if done is not None:
        done = 1 if done == u'true' else 0 
        kwargs = {'user_id':user_id,'id':id}
        updatekwargs = {'done':done}
        Todo.query.filter_by(**kwargs).update(updatekwargs)
        db_session.commit()
    return ('', 204)
