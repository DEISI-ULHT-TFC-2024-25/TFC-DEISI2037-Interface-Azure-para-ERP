import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pymysql
from azure_integration import criar_utilizador_azure, remover_utilizador_azure, obter_info_utilizador_logedIn, atualizar_utilizador_azure, obter_sku_id_por_nome, atribuir_licenca_ms365, remover_licenca_ms365, DOMAIN, TENANT_ID, AUTHORITY, CLIENT_ID, SCOPES 
from msal import PublicClientApplication

app = Flask(__name__)
CORS(app)

# Database connection details for OrangeHRM
DB_HOST = "192.168.0.213"
DB_USER = "orangehrm"
DB_PASSWORD = "orangehrm123"
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
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
            print(f"Connected to database, version: {db_version[0]}")
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

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


        # Adiciona um utilizador ao OrangeHRM e Azure
        if action == "add":
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            middle_name = data.get("middle_name", "")
            employee_id = data.get("employee_id", None)
            office_365_access = data.get("custom1", "No")
            sharepoint_access = data.get("custom2", "No")

            print(f"Inserting user: {first_name} {last_name}, {email}, custom1: {office_365_access}, custom2: {sharepoint_access}")

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
                criado = criar_utilizador_azure(email, first_name, last_name)

                if criado and office_365_access.strip().upper() == "YES":
                     sku_id = obter_sku_id_por_nome("OFFICE365_BUSINESS_PREMIUM")  #<--- Test
                     if sku_id:
                        atribuir_licenca_ms365(email.split("@")[0] + f"@{DOMAIN}", sku_id)
                        
                return jsonify({"message": "User added to OrangeHRM and Azure"}), 200
            except Exception as e:
                connection.rollback()
                return jsonify({"error": f"Error inserting user: {str(e)}"}), 500
            
            
        # Remove um utilizador ao OrangeHRM e Azure
        elif action == "remove":
            print(f"Removing user with email: {email}")

            # Primeiro obtemos os campos custom antes de apagar o registo da base de dados
            select_query = "SELECT custom1 FROM hs_hr_employee WHERE emp_work_email = %s"
            cursor.execute(select_query, (email,))
            result = cursor.fetchone()
            office_365_access = result[0] if result else "NO"

            delete_employee_query = """
            DELETE FROM hs_hr_employee WHERE emp_work_email = %s
            """

            try:
                # Se tiver licença, removemos antes de apagar o utilizador
                user_principal_name = email.split("@")[0] + f"@{DOMAIN}"
                if office_365_access.strip().upper() == "YES":
                    sku_id = obter_sku_id_por_nome("OFFICE365_BUSINESS_PREMIUM") 
                    if sku_id:
                        remover_licenca_ms365(user_principal_name, sku_id)

                # Depois apagamos da base de dados local
                cursor.execute(delete_employee_query, (email,))
                connection.commit()

                # E finalmente removemos o utilizador do Entra ID
                remover_utilizador_azure(email)

                return jsonify({"message": "User removed from OrangeHRM and Azure"}), 200

            except Exception as e:
                connection.rollback()
                return jsonify({"error": f"Error removing user: {str(e)}"}), 500

        # Update um utilizador ao OrangeHRM e Azure
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

                user_principal_name = email.split("@")[0] + f"@{DOMAIN}"
                sku_id = obter_sku_id_por_nome("OFFICE365_BUSINESS_PREMIUM")

                if sku_id:
                    if custom1.strip().upper() == "YES":
                        atribuir_licenca_ms365(user_principal_name, sku_id)
                    elif custom1.strip().upper() == "NO":
                        remover_licenca_ms365(user_principal_name, sku_id)

                atualizar_utilizador_azure(email, f"Updated {email}")  # opcional
                return jsonify({"message": "User updated in OrangeHRM and Azure"}), 200

            except Exception as e:
                connection.rollback()
                return jsonify({"error": f"Error updating user: {str(e)}"}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


# Recebe informação do utilizador logedIn no Entra ID
@app.route("/me", methods=["GET"])
def get_logged_in_user():
    
    try:
        app_msal = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        result = app_msal.acquire_token_interactive(scopes=SCOPES)

        if "access_token" not in result:
            return jsonify({"error": "Token not acquired"}), 401

        token = result["access_token"]
        user_data = obter_info_utilizador_logedIn(token)
        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9001)
