import sqlite3
import time
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'Secret123'

COLUMN_HEADERS = ['Sno', 'Name', 'Mobile', 'Balance', 'Password']

class Profile:
    def __init__(self, sno, name,account, phone, balance, password,pin):
        self.sno = sno
        self.name = name
        self.account=account
        self.phone = phone
        self.balance = balance
        self.password = password
        self.pin=pin
        self.attempts = 0

    def authentication_password(self, entered_password):
        if entered_password == self.password:
            return True
        else:
            return False
        
    def authentication_pin(self, entered_pin):
        if int(entered_pin) == self.pin:
            return True
        else:
            return False

    def print_balance(self):
        return self.balance

    def update_data(self):
        conn = sqlite3.connect('Bank_Final.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Users 
        SET Balance = ?, Password = ?
        WHERE Mobile = ?
        ''', (self.balance, self.password, self.phone))
        conn.commit()
        conn.close()

def get_user_by_mobile(mobile):
    conn = sqlite3.connect('Bank_Final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Mobile = ?", (mobile,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def load_data():
    conn = sqlite3.connect('Bank_Final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    conn.close()
    return data

def insert_data(account, name, mobile, password, pin):
    conn = sqlite3.connect('Bank_Final.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users(Name, Account, Mobile, Balance, Password, Pin) VALUES (?, ?, ?, 0, ?, ?)",
                   (name, account, mobile, password, pin))
    conn.commit()
    conn.close()


# Routes for the Flask application
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    mobile = request.form['mobile']
    password = request.form['password']
    pin = request.form['pin']

    user_data = get_user_by_mobile(mobile)

    if user_data:
        profile = Profile(*user_data)
        if profile.authentication_password(password):
            session['user'] = profile.phone  # Store the mobile number in the session
            return redirect(url_for('dashboard'))
        elif profile.authentication_pin(pin):
            session['user'] = profile.phone  # Store the mobile number in the session
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid password or pin! Please try again.", 'error')
            return redirect(url_for('home'))
    else:
        flash("Invalid mobile number! Please try again.", 'error')
        return redirect(url_for('home'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']
        pin = request.form['pin']

        # Validate name
        if re.search("[0-9]", name) or re.search("[!@#$%^&*_]", name):
            flash("Enter a proper name.", 'error')
            return redirect(url_for('create_account'))

        # Check if mobile number already exists
        data = load_data()
        for i in data:
            if i[3] == mobile:
                flash("This Phone Number is used by someone else. Try another number.", 'error')
                return redirect(url_for('create_account'))

        # Validate mobile number
        if len(mobile) != 10 or not mobile.isdigit():
            flash("Mobile must be a 10 digit number.", 'error')
            return redirect(url_for('create_account'))

        # Validate password
        if not (8 <= len(password) <= 16 and
                re.search("[a-z]", password) and re.search("[A-Z]", password) and
                re.search("[0-9]", password) and re.search("[!@#$%^&*_]", password)):
            flash("Password is not in a proper form.", 'error')
            return redirect(url_for('create_account'))

        # Validate PIN
        if len(pin) != 4 or not pin.isdigit():
            flash("Pin must be a 4 digit number.", 'error')
            return redirect(url_for('create_account'))

        account = int(time.time())
        insert_data(account, name, mobile, password, pin)
        flash("Account Created Successfully.", 'success')
        return redirect(url_for('home'))

    return render_template('create_account.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))

    phone = session['user']
    user_data = get_user_by_mobile(phone)
    if user_data:
        profile = Profile(*user_data)
        return render_template('dashboard.html', profile=profile)
    return redirect(url_for('home'))

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user' not in session:
        return redirect(url_for('home'))

    phone = session['user']
    user_data = get_user_by_mobile(phone)
    profile = Profile(*user_data)

    if request.method == 'POST':
        try:
            amount = int(request.form['amount'])
            profile.balance += amount
            profile.update_data()
            flash(f"Deposited {amount}. Your new balance is {profile.balance}", 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash("Invalid amount! Please enter a valid number.", 'error')

    return render_template('deposit.html', profile=profile)

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user' not in session:
        return redirect(url_for('home'))

    phone = session['user']
    user_data = get_user_by_mobile(phone)
    profile = Profile(*user_data)

    if request.method == 'POST':
        try:
            amount = int(request.form['amount'])
            if amount <= profile.balance:
                profile.balance -= amount
                profile.update_data()
                flash(f"Withdrew {amount}. Your new balance is {profile.balance}", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Insufficient funds!", 'error')
        except ValueError:
            flash("Invalid amount! Please enter a valid number.", 'error')

    return render_template('withdraw.html', profile=profile)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('home'))

    phone = session['user']
    user_data = get_user_by_mobile(phone)
    profile = Profile(*user_data)

    if request.method == 'POST':
        new_password = request.form['new_password']
        if new_password != profile.password and 8 <= len(new_password) <= 16 and \
           re.search("[a-z]", new_password) and re.search("[A-Z]", new_password) and \
           re.search("[0-9]", new_password) and re.search("[!@#$%^&*_]", new_password):
            profile.password = new_password
            profile.update_data()
            flash("Password changed successfully!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Password does not meet the criteria OR is the same as the old one.", 'error')

    return render_template('change_password.html', profile=profile)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

