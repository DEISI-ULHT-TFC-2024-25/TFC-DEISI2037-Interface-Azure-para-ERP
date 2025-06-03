import requests
from msal import ConfidentialClientApplication

# Configurações Azure AD
TENANT_ID = "<teu_tenant_id>"
CLIENT_ID = "<teu_client_id>"
CLIENT_SECRET = "<teu_client_secret>"
DOMAIN = "<teudominio>.onmicrosoft.com"  # Exemplo: minhaempresa.onmicrosoft.com

# Obter token de acesso

def obter_token():
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Erro ao obter token: {result}")

# Criar utilizador no Entra ID

def criar_utilizador_azure(email, nome, apelido):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    user_principal_name = email if email.endswith(f"@{DOMAIN}") else email.split("@")[0] + f"@{DOMAIN}"
    password = "qwe123"  # Pode ser gerado dinamicamente

    payload = {
        "accountEnabled": True,
        "displayName": f"{nome} {apelido}",
        "mailNickname": email.split("@")[0],
        "userPrincipalName": user_principal_name,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": password
        }
    }

    response = requests.post("https://graph.microsoft.com/v1.0/users", headers=headers, json=payload)
    if response.status_code == 201:
        print("Utilizador criado no Azure com sucesso.")
        return True
    else:
        print(f"Erro ao criar utilizador: {response.status_code} - {response.text}")
        return False

# Remover utilizador por UPN (userPrincipalName)
def remover_utilizador_azure(user_principal_name):
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}"

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("Utilizador removido com sucesso.")
        return True
    else:
        print(f"Erro ao remover utilizador: {response.status_code} - {response.text}")
        return False

# Atualizar utilizador (ex: mudar displayName ou atributos personalizados)
def atualizar_utilizador_azure(user_principal_name, novo_nome):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "displayName": novo_nome
    }

    response = requests.patch(
        f"https://graph.microsoft.com/v1.0/users/{user_principal_name}",
        headers=headers,
        json=payload
    )

    if response.status_code == 204:
        print("Utilizador atualizado com sucesso.")
        return True
    else:
        print(f"Erro ao atualizar utilizador: {response.status_code} - {response.text}")
        return False
