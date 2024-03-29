import requests
import os
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_ise_creds():
    global ise_pan, ise_user, ise_password
    ise_pan = os.environ.get("ISE_PAN")
    ise_user = os.environ.get("ISE_USER")
    ise_password = os.environ.get("ISE_PASSWORD")

    return ise_pan, ise_user, ise_password

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

def build_data_structure(ise_nodes):
    """Append Certificate list to it's node"""
    for node in ise_nodes:
        certs = get_certificates(node['name'])
        id = node["id"]
        node['certs'] = certs

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

def print_cert_list(ise_nodes):
    build_data_structure(ise_nodes)
    with open('dump.txt', 'w') as f:
       json.dump(ise_nodes, f, ensure_ascii=False, indent=4)

    for node in ise_nodes:
            print(f"\nretrieving certificates for {node['name']}")
            for list in node['certs']:
                print(f'ID: {list["id"]}, Name: {list["friendlyName"]}')
    return

def export_cert_list(ise_nodes):
    build_data_structure(ise_nodes)
    for node in ise_nodes:
            print(f"\nexporting certificates for {node['name']}")
            for list in node['certs']:
                print(f'Exporting ID: {list["id"]}, Name: {list["friendlyName"]}')
                export_certificate(list["id"], node)
    return

def export_certificate(id, node, certificate_password="C1sco12345", dir="cert_backup"):
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
    "hostName": f"{node['name']}", 
    "id": f"{id}",
    "password": f"{certificate_password}"
    }
    
    try:
        res = requests.post(url, headers=headers, verify=False, auth=(ise_user, ise_password), json=payload)
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err.response.text)
    
    filename = (res.headers.get("Content-Disposition").split("filename=")[1])
    
    if not os.path.isdir(dir): 
        os.mkdir(dir)
    
    open(f"{dir}/{filename}", 'wb').write(res.content)


def make_letsencrypt():
    pass

def make_adcs():
    pass

def expiration_check(ise_nodes):
    CERT_EXP_ALARM = 800
    build_data_structure(ise_nodes)
    now = datetime.now()
    for node in ise_nodes:
            print(f"\nChecking node: {node['name']}")
            for list in node['certs']:
                # print(f'Certificate ID: {list["id"]}, Expiration Date: {list["expirationDate"]}')
                # convert field into datetime object
                exp_date = datetime.strptime(list["expirationDate"], '%a %b %d %H:%M:%S %Z %Y')
                exp_delta = exp_date - now
                exp_delta = exp_delta.days
                if exp_delta < CERT_EXP_ALARM:
                    print(f'certificate {list["id"]} expires in {exp_delta} days!')
                


    return


def replace_expiring():
    pass

