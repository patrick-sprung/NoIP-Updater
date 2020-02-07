#!/usr/bin/env python3

import requests
import logging
from logging import handlers
import os
import traceback
import sys


# change to script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# No-IP
headers = {
    "User-agent": "Simple Python No-IP Updater/1.0 someone@somedomain.com"
}
url = "https://dynupdate.no-ip.com/nic/update"

# files
data_dir = "data"
log_dir = "log"
do_update_file = os.path.join(data_dir, "do_update.txt")
ip_file        = os.path.join(data_dir, "ip.txt")
cred_file      = os.path.join(data_dir, "credentials.txt")
log_file       = os.path.join(log_dir, "log.txt")

try:
    # create data and log directories
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    if not os.path.isfile(do_update_file):
        with open(do_update_file, "w") as f:
            f.write("yes")
    if not os.path.isfile(ip_file):
        with open(ip_file, "w") as f:
            f.write("0.0.0.0")
    if not os.path.isfile(cred_file):
        with open(cred_file, "w") as f:
            pass

    # init logger
    log = logging.getLogger("noip_updater")
    log.setLevel(10)
    frmt = logging.Formatter('[%(levelname)-5.5s] # [%(asctime)s] # %(message)s')
    file_handler = handlers.RotatingFileHandler(log_file, maxBytes=5242880, backupCount=3)
    file_handler.setFormatter(frmt)
    log.addHandler(file_handler)

    log.info("Started execution")

    # check that updates are enabled
    with open(do_update_file, "r") as f:
        content = f.read()
        if "y" not in content:
            log.warning("Update disabled. Check log.")
            raise StopIteration

    # read credentials
    with open(cred_file, "r") as f:
        creds = f.read().split("\n")
    if len(creds) != 5:
        log.error(f"Fill {cred_file} with necessary information.")
        raise StopIteration
    # Kabelbox
    kb_login_data = {
        "loginUsername": creds[0],
        "loginPassword": creds[1]
    }
    # No-IP
    host = creds[2]
    user = creds[3]
    passw = creds[4]

    # get IP address from the Kabelbox (router), adjust this for other environments
    # this is necessary because my ISP translates the address again
    # i.e. whatsmyipaddress returns wrong address
    with requests.Session() as s:
        s.post("https://192.168.0.1/goform/login", data=kb_login_data, verify=False)
        r = s.get("http://192.168.0.1/RgSwInfo.asp", verify=False)

        for line in r.text.split("\n"):
            if "IPv4 Address" in line and line.endswith("</div></div></div>"):
                line = line.rstrip("</div></div></div>")
                address = line[line.rfind(">")+1:]

    # compare to old IP
    with open(ip_file, "r") as f:
        old_address = f.read().strip(" \n")
    if old_address == address:
        log.info("Address hasn't changed. No update necessary.")
        raise StopIteration

    # update No-IP
    params = {
        "hostname": host,
        "myip": address
    }
    r = requests.get(url, params=params, headers=headers, auth=(user, passw))

    # update IP file, log results
    if r.status_code != 200:
        log.error(f"Status code: {r.status_code}")
    if r.text:
        if r.text.startswith("good") or r.text.startswith("nochg"):
            with open(ip_file, "w") as f:
                f.write(address)
            log.info(f"Update successful ({r.text}): {old_address} -> {address}")
        else:
            log.error(f"Response: {r.text}")
            log.error("Check www.noip.com/integrate/response for what above response means and fix the issue.")
            with open(do_update_file, "w") as f:
                f.write("no")

except StopIteration:
    pass
except ...:
    traceback.print_exception(*sys.exc_info(), file=log_file)
