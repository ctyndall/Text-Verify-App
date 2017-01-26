from flask import Flask, render_template, request, jsonify

import os
import sqlite3

import database_setup
import config
import helpers

app = Flask(__name__)

@app.route("/", methods=['GET'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return(render_template("register.html"))
    elif request.method == 'POST':
        to_number = request.form['mobile-number']
        course = request.form['class-name']
        name = request.form['name']
        if to_number == '' or course == '' or name == '':
            return render_template("register.html", message="Please fill out entire form.", mobile=to_number, course=course, name=name)
        pin = helpers.create_pin()
        try:
            helpers.add_user(to_number, name, course, pin)
        except sqlite3.IntegrityError:
            return render_template("register.html", message="Phone number already registered!")
        res = helpers.send_pin(to_number, pin)
        if res == "fail":
            return render_template("register.html", message="Oops! Something went wrong on our end.  Please try again.")
        return ('', 204)
        #return(render_template("verify.html", phone_number=to_number))

@app.route("/register-verify", methods=['POST'])
def verify_register():
    if request.method == 'GET':
        return(render_template("verify.html"))
    elif request.method == 'POST':
        pin = request.form['pin']
        number= request.form['mobile-number']
        if helpers.verify_pin(number, pin):
            return(render_template('success.html'))
        else:
            helpers.remove_user(number)  # user only gets one try to validate pin.  Otherwise, retry.
            return (render_template('register.html', message="Incorrect PIN.  Please register again."))

@app.route("/retrieve", methods=['GET', 'POST'])
def retrieve():
    if request.method == 'GET':
        return(render_template("retrieve.html"))
    elif request.method == 'POST':
        number = request.form['mobile-number']
        if number == '':
            return render_template("retrieve.html", message="Please input a number to lookup.")

        verified = helpers.check_user(number)
        if len(verified) == 0:
            return render_template("retrieve.html", message="Number not registered.")
        elif verified[0][0] != 1:  # sqlite response is tuple in a list. 1 means verified.
            return render_template("retrieve.html", message="Number is not yet verified!")
        new_pin = helpers.create_pin()
        helpers.update_pin(number, new_pin)
        res = helpers.send_pin(number, new_pin)
        if res == "fail":
            return render_template("retrieve.html", message="Oops! Something went wrong on our end.  Please try again.")
        return ('', 204)

@app.route("/verify-retrieve", methods=['POST'])
def verify_retrieve():
        print request.form
        number = request.form['mobile-number']
        pin = request.form['pin']
        print number, pin
        if helpers.verify_pin(number, pin):
            data = helpers.get_info(number)
            return(render_template("account-info.html", data=data))
        else:
            return(render_template("retrieve.html", message="Incorrect PIN.  Please retrieve another."))

if __name__ == "__main__":
    if not os.path.exists(database_setup.DB_FILENAME):
        database_setup.setup_database()
        
    app.config['SERVER_NAME'] = config.SERVER_NAME
    app.config['DEBUG'] = config.DEBUG
    app.run()