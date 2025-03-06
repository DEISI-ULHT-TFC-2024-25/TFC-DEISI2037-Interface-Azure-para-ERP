import mysql.connector
#test commit
# Configuração do banco de dados
DB_CONFIG = {
    'host': '192.168.0.213',
    'port': 3306,
    'user': 'orangehrm',
    'password': 'orangehrm123',
    'database': 'orangehrm_db',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'  # Define um collation compatível
}

# Nome da tabela
TABLE_NAME = 'hs_hr_employee'

def obter_email_disponiveis():
    """Função que lista os e-mails dos usuários cadastrados no banco"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"SELECT emp_number, emp_work_email FROM {TABLE_NAME} WHERE emp_work_email IS NOT NULL")
        emails = cursor.fetchall()

        if not emails:
            print("Nenhum e-mail encontrado no banco de dados.")
            return None

        print("\nLista de usuários disponíveis:")
        for emp_number, email in emails:
            print(f"ID: {emp_number} - Email: {email}")

        return emails

    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def atualizar_dados_por_email(email, novo_custom1, novo_custom2):
    """Função que atualiza os campos custom1 e custom2 com base no e-mail"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        update_query = f"""
        UPDATE {TABLE_NAME}
        SET custom1 = %s, custom2 = %s
        WHERE emp_work_email = %s
        """

        cursor.execute(update_query, (novo_custom1, novo_custom2, email))
        
        if cursor.rowcount > 0:
            print(f"Dados atualizados com sucesso para o e-mail {email}.")
        else:
            print("Nenhum registro foi atualizado. Verifique se o e-mail existe.")

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados ou atualizar os dados: {err}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# Fluxo do programa
emails_disponiveis = obter_email_disponiveis()
if emails_disponiveis:
    email_escolhido = input("\nDigite o e-mail do usuário que deseja atualizar: ").strip()
    novo_valor_custom1 = input("Digite o novo valor para custom1: ").strip()
    novo_valor_custom2 = input("Digite o novo valor para custom2: ").strip()

    atualizar_dados_por_email(email_escolhido, novo_valor_custom1, novo_valor_custom2)
