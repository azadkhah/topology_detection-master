import ipaddress
import json
import logging
import platform
import re
import traceback
from subprocess import Popen, PIPE

import requests
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def trace_ip_list(target_ips, th_num):
    logging.info(str(target_ips) + " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    uid_list = []
    logging.info(str(th_num) + " started")
    data_es = Elasticsearch(hosts='127.0.0.1:9200', timeout=2000, request_timeout=2000)
    # data_es = Elasticsearch(hosts='81.91.137.50:9200', timeout=2000, request_timeout=2000)
    for record in target_ips:
        try:
            route_list = []
            target_ip = record["ip"]
            s = Search(using=data_es, index="trace_route").query("match", _id=str(record["ip"]).strip())
            response = s.execute()
            URL = "https://dashboard.netseen.io/api/v1/topology/services/user-ranges?uid=" + record["uid"][0]
            logging.info("getting data from: " + URL)
            r = requests.get(url=URL)
            json_data = r.json()
            mask_list = []
            for doc in json_data:
                mask_list.append(doc["ip"] + "/" + str(doc["mask"]))
            mask = ""
            find = False
            if len(response["hits"]["hits"]) != 0:
                for qwe in mask_list:
                    if ipaddress.ip_address(record["ip"]) in ipaddress.ip_network(qwe, False):
                        mask = qwe[-2:]
                        if "mask" in response["hits"]["hits"][0]["_source"] and qwe[-2:] == \
                                response["hits"]["hits"][0]["_source"]["mask"]:
                            find = True
                            break

                    # logging.info("range added for uid: "+uid+" ---- "+doc["ip"]+"/"+str(doc["mask"]))
                if find:
                    logging.info("ip: " + target_ip + " traced before skip tracing ...")
                    continue
            else:
                for qwe in mask_list:
                    if ipaddress.ip_address(record["ip"]) in ipaddress.ip_network(qwe, False):
                        mask = qwe[-2:]
            logging.info("tracing: " + target_ip)
            c = 0
            count = 0
            logging.info("platform: " + str(platform.platform()))
            p = None
            if "windows" in platform.platform().strip().lower():
                p = Popen(['tracert', target_ip], stdout=PIPE)
            elif "linux" in platform.platform().strip().lower():
                p = Popen(['traceroute', target_ip], stdout=PIPE)
            while True:
                line = p.stdout.readline()
                count += 1
                if not line:
                    logging.info("end of process")
                    break
                fix_line = line.strip().decode("utf-8")
                ip = re.search(r'[0-9]+(?:\.[0-9]+){3}', fix_line)
                if ip and len(ip.group().split(".")) == 4:
                    c += 1
                    # logging.info(ip.group())
                    if (c == 1 and target_ip == ip.group()) or ip.group().startswith("192.168"):
                        # logging.info("first node or local router skipping: " + ip.group())
                        continue
                    route_list.append({"ip": ip.group(), "ttl": count})
                    if ip.group().__eq__(target_ip):
                        break
            if not route_list[-1]["ip"].__eq__(target_ip):
                route_list.append({"ip": target_ip, "ttl": count})
            final_doc = {}
            final_doc["route"] = route_list
            final_doc["ip"] = target_ip
            final_doc["ipaddr"] = target_ip
            final_doc["version"] = record["version"]
            final_doc["uid"] = record["uid"][0]
            final_doc["mask"] = mask
            if not record["uid"][0] in uid_list:
                uid_list.append(record["uid"][0])
            s = Search(using=data_es, index="trace_route").query("match", _id=str(record["ip"]).strip())
            response = s.execute()
            if len(response["hits"]["hits"]) != 0:
                logging.info("ip: " + target_ip + " traced before skip insreting ...")
                continue
            else:
                logging.info(final_doc)
                data_es.index("trace_route", id=str(target_ip).strip(), body=final_doc)
        except:
            logging.info(traceback.format_exc())
    with open("uid_" + str(th_num) + ".json", "w") as f:
        json.dump(uid_list, f)
