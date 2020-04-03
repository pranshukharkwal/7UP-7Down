from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt # Encrypt password
from functools import wraps
import string
import random

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

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def randomstring():
    N = 6
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
    return str(res)

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
                session['email'] = data['email']
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

@app.route('/referral' , methods=['GET' , 'POST'])
@is_logged_in
def referral():
    
    if request.method == 'POST':  #Enter someone's referral code

        username = session['username']
        ref_by_code = request.form['ref_by_code']

        try:
            cur = mysql.connection.cursor()

            #Getting referrer's id
            result = cur.execute('select * from referral where referral_code=%s' , [ref_by_code])  #this will show error if referral code does not exist
            referrer_id = cur.fetchone()['id']
            #Getting user's id
            result = cur.execute('select * from users where username = %s' , [username])
            user_id = cur.fetchone()['id']

            #Updating referred_by of user with referrer's code
            cur.execute('update referral set referred_by = %s where id = %s' , [ref_by_code , user_id])
            mysql.connection.commit()
            #Updating user's coins
            cur.execute('update users set coins = coins + 50 where username = %s' , [username]) #Update his coins
            mysql.connection.commit()
            #Updating referrer's coins
            cur.execute('update users set coins = coins + 50 where id = %s' , [referrer_id]) #Update referrer's coins
            mysql.connection.commit()
            #Updatomg referrers' referrals
            cur.execute('update referral set referrals = referrals + 1 where id = %s' , [referrer_id]) #Update referrer's referrals count
            mysql.connection.commit()

            #Getting referral data of user and sending it with render template
            result_ref = cur.execute('select * from referral where id = %s' , [id])
            ref_data = cur.fetchone()
            cur.close()
            flash('Referral code added successfully' , 'success')
            return render_template('referral.html' , ref_data = ref_data)
        except:

            result = cur.execute('select * from users where username = %s' , [username])
            user_id = cur.fetchone()['id']
            error = 'Referral Code does not exist'
            result_ref = cur.execute('select * from referral where id = %s' , [user_id])
            ref_data = cur.fetchone()
            return render_template('referral.html' , error = error , ref_data = ref_data)

    else:   #Generate every required data and send to the webpage

        username = session['username']
        cur = mysql.connection.cursor()
        result = cur.execute('select * from users where username = %s' , [username])
        id = cur.fetchone()['id']
        try:
            cur.execute('insert into referral(id) values(%s)' , [id])
        except:
            pass
        result_ref = cur.execute('select * from referral where id = %s' , [id])
        ref_data = cur.fetchone()

        if not ref_data['referral_code'] :  #One time task to generate referral code

                ref_code = randomstring()
                cur = mysql.connection.cursor()
                result = cur.execute('select * from users where username=%s' , [username])
                id = cur.fetchone()['id']
                if id > 0:
                    cur.execute('update referral set referral_code = %s where id = %s', (ref_code , id))
                else:
                    cur.execute('insert into referral(id , referral_code) values(%s , %s)' , (id , ref_code))
                mysql.connection.commit()

        if ref_data['referrals'] > 0:  #To fetch the list of people who have entered user's referral code

                ref_code = ref_data['referral_code']
                ref_result = cur.execute('select name from users u , referral r where u.id = r.id and r.referred_by = %s' , [ref_code])
                names = cur.fetchall()
                cur.close()
                return render_template('referral.html' , ref_data=ref_data , names = names)

        else : #If the user has no referrals
            cur.close()
            return render_template('referral.html' , ref_data = ref_data)

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
    return render_template('dashboard.html', data=data)

@app.route('/referral_system')
def referral_system():
    return render_template('referral_system.html')

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

@app.route('/leaderboard')
def leaderboard():
   
    if 'logged_in' in list(session.keys()) :
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT name, username, email, coins FROM users Order By coins Desc")
        data = cur.fetchall()
        result1 = cur.execute("Select name, username, email, coins from users where username = %s",[session['username']])
        logged_in = cur.fetchone()
        cur.close()
        return render_template('leaderboard.html', data=data, user = logged_in)
    else:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT name, username, email, coins FROM users Order By coins Desc")
        data = cur.fetchall()
        cur.close()
        return render_template('leaderboard.html', data=data)

    # fetchmany(number of rows) fetches number of rows
    # fetchone() fetches one row
    # fetchall() fetchall rows from the 
    
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
