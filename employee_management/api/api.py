from flask import Flask, request, jsonify
from datetime import date
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import random

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# Enter Your MySQL DB Password below.
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_db'

mysql = MySQL(app)


def generate_emp_id():
    random_id = random.randint(1000001, 1999999)
    cur = mysql.connection.cursor()
    val = cur.execute(f"SELECT * FROM employee_tab WHERE emp_id={random_id}")
    cur.close()
    if val > 0:
        generate_emp_id()
    elif val == 0:
        return random_id


@app.route("/add_employee", methods=['POST'])
def add_employee_to_db():
    if request.method == 'POST':
        try:
            employee = request.get_json()
            emp_id = generate_emp_id()
            name = employee['name']
            gender = employee['gender']
            address = employee['address']
            dob = employee['dob']
            mobile = employee['mobile']
            email = employee['email']
            role = 'Employee'
            if name == "":
                return jsonify({
                    "status": "error",
                    "msg": "Name field could not be empty."
                }), 200
            elif address == "":
                return jsonify({
                    "status": "error",
                    "msg": "Address field could not be empty."
                }), 200
            elif dob == "":
                return jsonify({
                    "status": "error",
                    "msg": "DOB field could not be empty."
                }), 200
            elif mobile == "":
                return jsonify({
                    "status": "error",
                    "msg": "Mobile field could not be empty."
                }), 200
            elif email == "":
                return jsonify({
                    "status": "error",
                    "msg": "Email field could not be empty."
                }), 200
            else:
                actual_password = str(dob[0:2]+dob[3:5]+dob[6:10])
                password = sha256_crypt.encrypt(actual_password)
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO employee_tab(emp_id, name, gender, address, dob, mobile, email, role, password) "
                            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);", (emp_id, name, gender, address, dob, mobile, email, role, password))
                mysql.connection.commit()
                cur.close()
            return jsonify({
                "status": "Employee successfully added",
                "data": employee
            }), 200
        except mysql.connection.DataError as err:
            return jsonify({
                "status": "error",
                "msg": "Entered data is too long."
            }), 200
        except mysql.connection.IntegrityError as err:
            return jsonify({
                "status": "error",
                "msg": "Email id already present in database."
            }), 200


def calculate_age(dob):
    age = 0
    day = int(dob[0:2])
    month = int(dob[3:5])
    year = int(dob[6:10])
    today = date.today()
    if today.year > year:
        if today.month > month:
            age = today.year - year
        elif today.month == month:
            if today.day > day:
                age = today.year - year
            else:
                age = today.year - year - 1
        else:
            age = today.year - year - 1
    return age


@app.route("/search_employee", methods=['GET', 'POST'])
def search_employee():
    if request.method == "POST":
        data = request.get_json()
        emp_id = data["emp_id"]
        name = data["name"]
        age = data["age"]
        location = data["location"]
        cur = mysql.connection.cursor()
        val = cur.execute("SELECT * FROM employee_tab")
        emp_data = cur.fetchall()
        lst = []
        emp = ()

        binary_list = []
        if name == "":
            binary_list.append(0)
        else:
            binary_list.append(1)
        if age == "":
            binary_list.append(0)
        else:
            binary_list.append(1)
        if location == "":
            binary_list.append(0)
        else:
            binary_list.append(1)

        binary = int(str(str(lst[0])+str(lst[1])+str(lst[2])), 2)

        if emp_id != "":
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE emp_id={emp_id};")
            emp = cur.fetchone()
        elif emp_id == "" and binary == 0:
            return jsonify({
                "status": "error",
                "msg": "All fields could not be empty."
            }), 200
        elif binary == 1:
            #location
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE location like '%{location}%';")
            emp = cur.fetchall()
        elif binary == 2:
            #age
            for i in emp_data:
                if calculate_age(i[4]) == age:
                    lst.append(i)
            emp = tuple(lst)
        elif binary == 4:
            #name
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE name like '{name}%';")
            emp = cur.fetchall()

        elif binary == 3:
            #location, age
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE location like '%{location}%';")
            emp = cur.fetchall()
            for i in emp:
                if calculate_age(i[4]) == age:
                    lst.append(i)
            emp = tuple(lst)
        elif binary == 5:
            #name, location
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE name like '{name}%' and location like '%{location}%';")
            emp = cur.fetchall()
        elif binary == 6:
            #name, age
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE name like '{name}%';")
            emp = cur.fetchall()
            for i in emp:
                if calculate_age(i[4]) == age:
                    lst.append(i)
            emp = tuple(lst)
        elif binary == 7:
            #ame, age , location
            cnt = cur.execute(f"SELECT * FROM employee_tab WHERE name like '{name}%' and location like '%{location}%';")
            emp = cur.fetchall()
            for i in emp:
                if calculate_age(i[4]) == age:
                    lst.append(i)
            emp = tuple(lst)
        cur.close()
        return jsonify({
            "status": "success",
            "data": emp,
        }), 200


@app.route("/get_all_employee", methods=['GET'])
def get_all_employee():
    cur = mysql.connection.cursor()
    val = cur.execute("SELECT * FROM employee_tab")
    emp_data = cur.fetchall()
    cur.close()
    return jsonify({
            "status":"success",
            "data": emp_data,
        }), 200


@app.route(f"/delete_employee/id/<id>")
def delete_employee(emp_id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM employee_tab WHERE emp_id={emp_id};")
    mysql.connection.commit()
    cur.close()
    return jsonify({
            "status": "success",
            "msg": "Employee deleted successfully"
            
        }), 200


@app.route("/get_employee/<emp_id>", methods=['GET'])
def get_employee(emp_id):
    cur = mysql.connection.cursor()
    val = cur.execute(f"SELECT * FROM employee_tab WHERE emp_id={emp_id};")
    emp_data = cur.fetchone()
    cur.close()
    if val == 0:
        return jsonify({
            "status": "error",
            "msg": "Employee not found."
        }), 200
    else:
        return jsonify({
            "status": "success",
            "data": {'emp_id':emp_data[0], 'name':emp_data[1], 'gender': emp_data[2], 'address': emp_data[3],
                     'dob': emp_data[4], 'mobile': emp_data[5], 'email': emp_data[6], 'role': emp_data[7]},
        }), 200


@app.route("/update_employee/<emp_id>", methods=['PUT'])
def update_employee(emp_id):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            name = data['name']
            gender = data['gender']
            address = data['address']
            dob = data['dob']
            mobile = data['mobile']
            email = data['email']
            if name == "":
                return jsonify({
                    "status": "error",
                    "msg": "Name field could not be empty."
                }), 200
            elif address == "":
                return jsonify({
                    "status": "error",
                    "msg": "Address field could not be empty."
                }), 200
            elif dob == "":
                return jsonify({
                    "status": "error",
                    "msg": "DOB field could not be empty."
                }), 200
            elif mobile == "":
                return jsonify({
                    "status": "error",
                    "msg": "Mobile field could not be empty."
                }), 200
            elif email == "":
                return jsonify({
                    "status": "error",
                    "msg": "Email field could not be empty."
                }), 200
            else:
                actual_password = str(dob[0:2]+dob[3:5]+dob[6:10])
                password = sha256_crypt.encrypt(actual_password)
            cur = mysql.connection.cursor()
            cur.execute(f"UPDATE employee_tab SET name=%s, gender=%s, address=%s, dob=%s, mobile=%s, email=%s, password=%s "
                        f"WHERE emp_id={emp_id};", (name, gender, address, dob, mobile, email, password))
            mysql.connection.commit()
            cur.close()
            return jsonify({
                "status": "success",
                "msg": "Employee details updated successfully",
            }), 200
        except mysql.connection.DataError as err:
            return jsonify({
                "status": "error",
                "msg": "Entered data is too long."
            }), 200
        except mysql.connection.IntegrityError as err:
            return jsonify({
                "status": "error",
                "msg": "Email id already present in database."
            }), 200



@app.route("/authenticate_user",methods=["POST"])
def authenticate_user():
    user_detail=request.get_json()
    email=user_detail["email"]
    passwordEntered = user_detail['password']
    # print(email,passwordEntered)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM employee_tab WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    if user:
        passwordInDb=user[-1]
        isUser = sha256_crypt.verify(passwordEntered,passwordInDb)
        if(isUser):
            return jsonify({
                "status":"success",
                "msg":"User is authenticated",
                "data":user,
            }),200
        else:
             return jsonify({
                "status":"error",
                "msg":"Wrong password",
                "data":user,
            }),200
    return jsonify({
                "status":"error",
                "msg":"email doesn't exist",
            }),200


if __name__ == '__main__':
    app.run(debug=True)