import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# Database connection details for OrangeHRM
DB_HOST = "192.168.0.213"
DB_USER = "orangehrm"  # Replace with your database username
DB_PASSWORD = "orangehrm123"  # Replace with your database password
DB_NAME = "orangehrm_db"

def connect_to_db():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=3306
        )
        # Check connection by running a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")  # Just check the database version as a test
            db_version = cursor.fetchone()
            print(f"Connected to database, version: {db_version[0]}")
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

# OrangeHRM user management via Database
@app.route('/manage-user-orangehrm', methods=['POST'])
def manage_user_orangehrm():
    try:
        data = request.json
        email = data.get("email")
        action = data.get("action")

        connection = connect_to_db()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()

        if action == "add":
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            middle_name = data.get("middle_name", "")  # Optional field
            employee_id = data.get("employee_id", None)  # Optional unique ID
            office_365_access = data.get("custom1", "No")  # Yes or No
            sharepoint_access = data.get("custom2", "No")  # Yes or No

            print(f"Inserting user: {first_name} {last_name}, {email}, custom1: {office_365_access}, custom2: {sharepoint_access}")

            # Insert employee into the `hs_hr_employee` table
            insert_employee_query = """
            INSERT INTO hs_hr_employee (
                emp_number, employee_id, emp_lastname, emp_firstname, emp_middle_name,
                emp_work_email, custom1, custom2
            )
            VALUES (
                NULL, %s, %s, %s, %s, %s, %s, %s
            )
            """
            try:
                cursor.execute(insert_employee_query, (
                    employee_id, last_name, first_name, middle_name, email, office_365_access, sharepoint_access
                ))
                connection.commit()
                print("User added successfully.")
                return jsonify({"message": "User added to OrangeHRM"}), 200
            except Exception as e:
                print(f"Error executing insert query: {e}")
                connection.rollback()  # Rollback if there's an error
                return jsonify({"error": f"Error inserting user: {str(e)}"}), 500

        elif action == "remove":
            print(f"Removing user with email: {email}")

            # Delete employee based on work email
            delete_employee_query = """
            DELETE FROM hs_hr_employee WHERE emp_work_email = %s
            """
            try:
                cursor.execute(delete_employee_query, (email,))
                connection.commit()
                print("User removed successfully.")
                return jsonify({"message": "User removed from OrangeHRM"}), 200
            except Exception as e:
                print(f"Error executing delete query: {e}")
                connection.rollback()  # Rollback if there's an error
                return jsonify({"error": f"Error removing user: {str(e)}"}), 500

        elif action == "update":
            custom1 = data.get("custom1", "No")
            custom2 = data.get("custom2", "No")
            print(f"Updating user with email: {email}, custom1: {custom1}, custom2: {custom2}")

            update_employee_query = """
            UPDATE hs_hr_employee 
            SET custom1 = %s, custom2 = %s 
            WHERE emp_work_email = %s
            """
            try:
                cursor.execute(update_employee_query, (custom1, custom2, email))
                connection.commit()
                print("User updated successfully.")
                return jsonify({"message": "User updated in OrangeHRM"}), 200
            except Exception as e:
                print(f"Error executing update query: {e}")
                connection.rollback()
                return jsonify({"error": f"Error updating user: {str(e)}"}), 500


        return jsonify({"error": "Invalid action"}), 400

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9001)
