import requests
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# pega os ip's maliciosos no abuse
def get_blacklist():
    api_key = os.getenv("abuse_apikey")
    url = "https://api.abuseipdb.com/api/v2/blacklist"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    params = {
        "confidenceMinimum": 30,
        "limit": 9999999,
        "ipVersion": 4
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        
        data = response.json().get("data", [])
        ip_addresses = [ip["ipAddress"] for ip in data]
        return ip_addresses
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Retorna a mensagem de erro

# helix
def get_access_token( ):
    url = 'https://auth.trellix.com/auth/realms/IAM/protocol/openid-connect/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'scope': os.getenv('scopes'),
        'grant_type': 'client_credentials'
    }

    auth=(os.getenv('client_id'),os.getenv('client_secret'))
    
    try:
        response = requests.post(url, headers=headers, data=data, auth=auth)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        
        if response.status_code == 200:
            return response.json()['access_token']  # Retorna o token de acesso
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Retorna a mensagem de erro

    return {"error": response.status_code, "message": response.text}  # Retorna erro se não for 200

# pega a lista malicous_ip
def get_malicious_ip_list():
    try:
        response = requests.get(
            url='https://xdr.trellix.com/helix/id/hexfvb734/api/v3/lists/?name=malicious_ip', 
            headers={
                'accept': 'application/json',
                'x-trellix-api-token': f'Bearer {get_access_token()}'
            }
        )
        
        if response.status_code == 200:
            return response.json()  # Retorna a lista de IPs maliciosos
        else:
            return {"error": response.status_code, "message": response.text}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Retorna a mensagem de erro

# adiciona o ip na lista do helix
def add_list(ip):
    try:
        response = requests.post(
            url=f'https://xdr.trellix.com/helix/id/hexfvb734/api/v3/lists/{os.getenv("helix_list")}/items/',
            headers={
                'accept': 'application/json',
                'x-trellix-api-token': f'Bearer {get_access_token()}'
            },
            json={
                'value': ip,
                'type': 'misc',
                'risk': 'Medium',
                'notes': 'secdevops',
                'list': int(os.getenv('helix_list'))
            }
        )

        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}
    except requests.exceptions.RequestException as e:  # Captura exceções de requisições
        return {"error": str(e)}  # Retorna a mensagem de erro

# loop
lista = get_blacklist()
print('Lista Carregada')
for ip in lista:
    print(add_list(ip))
print("Adicionado todos os IP's")