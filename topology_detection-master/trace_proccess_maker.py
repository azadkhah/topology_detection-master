import json
import logging
import threading
import time
import traceback

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

import draw_topology
from trace_child import trace_ip_list


def pre_version_checker(start_version, end_version, th_count):
    for i in range(start_version, end_version):
        p_maker(i, th_count)


def p_maker(version, th_count):
    logging.info("p_maker for trace is stared version: "+str(version))
    data_es = Elasticsearch(hosts='127.0.0.1:9200', timeout=2000, request_timeout=2000)
    # data_es = Elasticsearch(hosts='81.91.137.50:9200', timeout=2000, request_timeout=2000)
    main_es = Elasticsearch(hosts='81.91.132.134:9200', timeout=2000, request_timeout=2000)
    if not data_es.indices.exists(index="trace_route"):
        mapping = {
            "mappings": {
                "properties": {
                    "ipaddr": {
                        "type": "ip"
                    }
                }
            }
        }
        data_es.indices.create(index="trace_route", body=mapping)

    hit_list = []
    th_list = []
    hit_map = {}
    for i in range(0, th_count):
        hit_map[i] = []

    c = 0
    s = Search(using=main_es, index="custom_ip_records").query("match", version=version)
    for hit in s.scan():
        try:
            hit_map[c].append(hit)
            c += 1
            c %= th_count
        except:
            logging.info(traceback.format_exc())

    # logging.info(hit_map)
    for i in range(0, th_count):
        x = threading.Thread(target=trace_ip_list, args=(hit_map[i], i,))
        x.start()
        logging.info("thread " + str(i) + " start called")
        th_list.append(x)
    end = False
    while not end:
        time.sleep(10)
        for th in th_list:
            if th.is_alive():
                logging.info("tracing threads are alive")
                break
            end = True
    # time.sleep(5)
    uid_list = []
    for i in range(0, th_count):
        try:
            with open('uid_' + str(i) + '.json') as f:
                sub_uid_list = json.load(f)
                for uid in sub_uid_list:
                    try:
                        if not uid in uid_list:
                            uid_list.append(uid)
                    except:
                        logging.info(traceback.format_exc())
        except:
            logging.info(traceback.format_exc())

    for uid in uid_list:
        draw_topology.draw_with_uid(uid)
