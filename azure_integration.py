import requests
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv
load_dotenv()


# Configurações Azure AD
TENANT_ID = "138ccc06-516b-4e81-8813-06fd2531bddc"
CLIENT_ID = "13d580a1-6f88-488c-87cc-b9e5ebf5e1d3"
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")   
DOMAIN = "grupolusofona.onmicrosoft.com" 

# Função para obter o token de acesso
def obter_token():
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        print("Token obtido com sucesso.")
        return result["access_token"]
    else:
        raise Exception(f"Erro ao obter token: {result}")

#Obter SKU ID por nome de licença
def obter_sku_id_por_nome(nome_licenca):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}"
        }

    response = requests.get("https://graph.microsoft.com/v1.0/subscribedSkus", headers=headers)
    if response.status_code == 200:
        skus = response.json().get("value", [])
        for sku in skus:
            if sku["skuPartNumber"].lower() == nome_licenca.lower():
                return sku["skuId"]
    else:
        print("Erro ao obter licenças disponíveis:", response.status_code, response.text)
    return None

# Atribuir licença Microsoft 365 a um utilizador
def atribuir_licenca_ms365(user_principal_name, sku_id):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "addLicenses": [{"skuId": sku_id}],
        "removeLicenses": []
    }

    url = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/assignLicense"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Licença atribuída com sucesso.")
        return True
    else:
        print("Erro ao atribuir licença:", response.status_code, response.text)
        return False

# Remover licença Microsoft 365 de um utilizador
def remover_licenca_ms365(user_principal_name, sku_id):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "addLicenses": [],
        "removeLicenses": [sku_id]
    }

    url = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/assignLicense"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Licença removida com sucesso.")
        return True
    else:
        print(f"Erro ao remover licença: {response.status_code} - {response.text}")
        return False


# Criar utilizador no Entra ID
def criar_utilizador_azure(email, nome, apelido):
    token = obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    user_principal_name = email if email.endswith(f"@{DOMAIN}") else email.split("@")[0] + f"@{DOMAIN}"
    password = "qwe123"  

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


criar_utilizador_azure("tiago.a@gmail.com ", "Tiago", "Amaro") #teste