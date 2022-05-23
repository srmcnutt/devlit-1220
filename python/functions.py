import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ise_pan = os.environ.get("ISE_PAN")
ise_user = os.environ.get("ISE_USER")
ise_password = os.environ.get("ISE_PASSWORD")


def get_nodes(ise_pan, ise_user, ise_password):
    """
    gets all of the nodes in the deployment
    """

    url=f"https://{ise_pan}/ers/config/node"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    ise_nodes = []

    try:
        res = requests.get(url, headers=headers, verify=False, auth=(ise_user, ise_password))
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    nodes = res.json()
    ise_nodes = []

    for node in nodes["SearchResult"]["resources"]:
        ise_nodes.append(node)
    return ise_nodes

def get_certificates(node):
    """
    gets all of the nodes in the deployment
    """
    url=f"https://{ise_pan}/api/v1/certs/system-certificate/{node}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, verify=False, auth=(ise_user, ise_password))
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    certificates = res.json()["response"]

    return certificates

def export_certificates(id, certificate_password="C1sco12345", dir="cert_backup"):
    """
    Export all the system certificates on a node
    and store them on disk
    """

    url=f"https://{ise_pan}/api/v1/certs/system-certificate/export"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
    "export": "CERTIFICATE_WITH_PRIVATE_KEY",
    "id": f"{id}",
    "password": f"{certificate_password}"
    }

    try:
        res = requests.post(url, headers=headers, verify=False, auth=(ise_user, ise_password), json=payload)
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    filename = (res.headers.get("Content-Disposition").split("filename=")[1])
    
    if not os.path.isdir(dir): 
        os.mkdir(dir)
    
    open(f"{dir}/{filename}", 'wb').write(res.content)


def make_letsencrypt():
    pass

def make_adcs():
    pass

def expiration_check():
    pass

def replace_expiring():
    pass

