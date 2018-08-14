from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash
    )
from flask_paginate import (
    Pagination, 
    get_page_parameter 
)


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

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    user_id = session['user']['id']
    cur = g.db.execute("SELECT * FROM todos where user_id = '%s'" % user_id)
    todos = cur.fetchall()
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
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    desc =  request.form.get('description', '')
    if len(desc) > 0:
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], request.form.get('description', ''))
        )
        g.db.commit()
        flash(u'Todo item successfully created','success')
    else:
        flash(u'Todo item not created. Description is requireid.','error')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    user_id = session['user']['id']
    g.db.execute("DELETE FROM todos WHERE id ='%s' and user_id ='%s'" % (id,user_id) )
    g.db.commit()
    flash(u'Todo successfully deleted','success')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['PATCH'])
def todos_patch(id):
    if not session.get('logged_in'):
        return redirect('/login')
    user_id = session['user']['id']
    done = request.form.get("done",None)
    if done is not None:
        done = 1 if done == u'true' else 0 
        g.db.execute("UPDATE todos set done = %d WHERE id ='%s' and user_id ='%s'" % (done,id,user_id) )
        g.db.commit()
    return ('', 204)
