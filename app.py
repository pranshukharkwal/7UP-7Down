from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt # Encrypt password
from functools import wraps
# ctrl+shift+r to clear the cache of the browser and see the changes done.
app = Flask(__name__)
app.secret_key='secret123'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'JJFKCXD3CC'
app.config['MYSQL_PASSWORD'] = 'us8bg5jdXp'
app.config['MYSQL_DB'] = 'JJFKCXD3CC'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

@app.route('/test')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register' , methods=['GET' , 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))

            cur = mysql.connection.cursor()
            cur.execute('insert into users(name , username , email , password) values(%s , %s , %s , %s)', (name , username , email , password))
            mysql.connection.commit()
            cur.close()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        except:
            error = 'Username already exists. Choose another'
            return render_template('register.html' , error = error , form = form)
    return render_template('register.html' , form=form)

@app.route('/login' , methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in' , 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html' , error = error)
        else:
            error = 'Username not found'
            return render_template('login.html' , error = error)
        cur.close()
    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():
    if request.method == 'POST':
        data = request.get_json()
        app.logger.info(data)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE username = %s", [session['username']])
    data = cur.fetchone()
    cur.close()
    print('Rohan Raj Kansal')
    return render_template('dashboard.html', data=data)

@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        print('Post Request')
        data = request.get_json()
        cur = mysql.connection.cursor()
        print('Successful Connection!!')
        print(data)
        cur.execute('update users set coins = %s where id = %s', (data['coins'],data['id']))
        mysql.connection.commit()
        # result = cur.execute('Select * from users where id = %s',[data['id']]) # [] are used if we are using only one value or (value,) making it iterable
        # print('Extracted Completely!')
        # final_result = cur.fetchone()
        cur.close()
        return redirect(url_for('dashboard'))


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug = True)
