from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'loginpage',
}

# Helper function to establish a database connection
def get_db_connection():
    conn = pymysql.connect(**db_config)
    return conn

s_time = "Apr 7, 2024 1:30:25"
end_time = "Sep 27, 2024 1:30:25"

def count(): 
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM questions;")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            if password == user[3]:
                session['name'] = user[0]
                session['lname'] = user[1]
                session['email'] = user[2]
                session['username'] = user[6]
                session['user_marks'] = 0
                session['i'] = 1
                return render_template("home.html")
            else:
                return "Error: password and email do not match"
        else:
            return "Error: user not found"
    else:
        return render_template("login.html")

@app.route('/ps_login',methods=["GET","POST"])
def ps_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "mkavyasri18@gmail.com" and password == "password":
            session['ps'] = 1
            return redirect(url_for('ps_portal'))
        else:
            return "Error: password or email do not match"
    else:
        return render_template("ps_login.html")

@app.route('/ps_logout')
def ps_logout():
    session['ps'] = 0
    return redirect(url_for('home'))

@app.route('/ps_portal', methods=["GET","POST"])
def ps_portal():
    total_Q = count()
    session['q'] = total_Q[0] + 1
    if request.method == 'POST':
        q_no = request.form['q_no']
        question = request.form['question']
        a = request.form['A']
        b = request.form['B']
        c = request.form['C']
        d = request.form['D']
        correct_option = request.form['Correct_answer']
        marks = request.form['marks']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO questions VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", (q_no, question, a, b, c, d, correct_option, marks))
        conn.commit()
        cur.close()
        conn.close()
        return render_template("ps_portal.html", total=total_Q[0] + 2)
    else:
        return render_template("ps_portal.html", total=total_Q[0] + 1)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        fname = request.form['first_name']
        lname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        dob = request.form['birthday']
        username = request.form['username']
        phone = request.form['phone']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (fname, lname, email, password, gender, dob, username, phone))
        cur.execute("INSERT INTO leaderboard(username) VALUES (%s)", (username,))
        conn.commit()
        cur.close()
        conn.close()
        session['fname'] = fname
        session['email'] = email
        return redirect(url_for('login'))

@app.route('/Developer')
def developer():
    return render_template("Developer.html")

@app.route('/instructions')
def instruction():   
    total_Q = count()
    for k in range(1, total_Q[0] + 1):
        l = str(k)
        session[l] = 0
    return render_template("instructions.html", sTime=s_time, eTime=end_time, total_Q=total_Q[0])

@app.route('/questions', methods=["GET", "POST"])
def questions():
    total_Q = count()

    if request.method == 'POST':
        opt = request.form['option']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT correct_answer,marks FROM questions WHERE q_no=%s;", (session['i'],))
        x = cur.fetchone()
        cur.close()
        conn.close()

        k = str(session['i'])
        if opt == x[0] and session[k] == 0:
            session['user_marks'] += x[1]
            session[k] = 1
        elif opt != x[0] and session[k] == 1:
            session['user_marks'] -= x[1]
            session[k] = 0

        return render_template("question.html", sTime=s_time, eTime=end_time, total_Q=total_Q[0])
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT q_no,question,a,b,c,d,marks FROM questions WHERE q_no=%s", (session['i'],))
        data = cur.fetchone()
        cur.close()
        conn.close()

        if data:
            session['q_no'] = data[0]
            session['Q'] = data[1]
            session['A'] = data[2]
            session['B'] = data[3]
            session['C'] = data[4]
            session['D'] = data[5]
            session['q_mark'] = data[6]

        return render_template("question.html", sTime=s_time, eTime=end_time, total_Q=total_Q[0])

@app.route('/next')
def Next():
    total_Q = count()
    
    if session['i'] == total_Q[0]:
        return redirect(url_for('questions'))
    else:
        session['i'] += 1
    return redirect(url_for('questions'))

@app.route('/prev')
def prev():
    if session['i'] == 1:
        return redirect(url_for('questions'))
    else:
        session['i'] -= 1
    return redirect(url_for('questions'))

@app.route('/final_submit')
def final_submit():
    global user_marks
    session['i'] = 1
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT marks FROM questions;")
    x = cur.fetchall()
    conn.commit()
    cur.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE leaderboard SET marks=%s WHERE username=%s;", (session['user_marks'], session['username']))
    conn.commit()
    cur.close()

    y = list(sum(x, ()))
    total_marks = sum(y)
    session['total_marks'] = total_marks
    user_marks = 0
    return render_template("result.html")

@app.route('/results')
def results():
    return render_template("result.html")

@app.route('/ps_view', methods=["GET","POST"])
def ps_view():
    if request.method == 'GET':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT q_no, question, a, b, c, d, correct_answer, marks FROM questions;")
        Qdata = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('ps_view.html', Qdata=Qdata)
    else:
        return render_template('ps_view.html')

@app.route('/edit_q', methods=["POST"])
def edit_q():
    q_no = request.form['edit']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, a, b, c, d, correct_answer, marks FROM questions WHERE q_no=%s;", (q_no,))
    Qdata = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit.html", total=q_no, Qdata=Qdata)

@app.route('/edit', methods=["POST"])
def edit():
    q_no = request.form['q_no']
    question = request.form['question']
    a = request.form['A']
    b = request.form['B']
    c = request.form['C']
    d = request.form['D']
    correct_option = request.form['Correct_answer']
    marks = request.form['marks']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE questions SET question = %s, a = %s, b = %s, c = %s, d = %s, correct_answer = %s, marks =%s WHERE q_no = %s", (question, a, b, c, d, correct_option, marks, q_no))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('ps_view'))

@app.route('/delete_q', methods=["POST"])
def delete_q():
    q_no = request.form['delete']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE q_no=%s;", (q_no,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('ps_view'))

@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select username,marks,fname,lname from leaderboard natural join users where username = username order by marks desc;")
    Ldata = cur.fetchall()
    conn.commit()
    cur.close()
    print(Ldata)
    size = len(Ldata)

    List1 = []
    for i,_ in enumerate(Ldata):
        List1.append(Ldata[i] + (i+1,)) 

    return render_template('leaderboard.html',data=List1)
    


@app.route('/myprofile')
def myprofile():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT fname, lname, gender, dob, username, phone FROM users WHERE email=%s;", (session['email'],))
    Pdata = cur.fetchone()  # Fetch user profile data from the database
    cur.close()
    conn.close()
    
    if Pdata:
        session['fname'] = Pdata[0]
        session['lname'] = Pdata[1]
        return render_template('myprofile.html', Pdata=Pdata)  # Pass the profile data to the template
    else:
        return "Error: User not found"

@app.route('/reset_lb', methods=["POST"])
def clear_lb():
    # Include your database configuration here
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Add the password here
        'database': 'loginpage'  # Add your database name here
    }

    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    cur.execute("UPDATE leaderboard SET marks=0;")
    conn.commit()
    cur.close()
    conn.close()  # Make sure to close the connection
    return "success"


@app.route('/test_timings',methods=["POST","GET"])
def test_timings():
    global s_time
    global end_time

    if request.method == 'POST':
        s_time = request.form['s_time']
        end_time = request.form['end_time']

        return render_template("set_time.html",sTime = s_time,eTime = end_time)
    else :
        return render_template("set_time.html",sTime = s_time,eTime = end_time)

@app.route('/prohibited')
def prohibited():
    global s_time
    return render_template("prohibited.html",sTime = s_time)        

    
    



if __name__ == '__main__':
    app.secret_key = '^A%DJAJU^JJ123'  # Replace 'your_secret_key' with a real secret key
    app.run(debug=True)
