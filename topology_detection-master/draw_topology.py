import ipaddress
import json
import logging
import time
import traceback

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

import dfs
import requests

# import socket,struct
#
# def makeMask(n):
#     "return a mask of n bits as a long integer"
#     return (2L<<n-1) - 1
#
# def dottedQuadToNum(ip):
#     "convert decimal dotted quad string to long integer"
#     return struct.unpack('L',socket.inet_aton(ip))[0]
#
# def networkMask(ip,bits):
#     "Convert a network address to a long integer"
#     return dottedQuadToNum(ip) & makeMask(bits)
#
# def addressInNetwork(ip,net):
#     "Is an address in a network"
#     return ip & net == net

# address = dottedQuadToNum("192.168.1.1")
# networka = networkMask("10.0.0.0",24)
# networkb = networkMask("192.168.0.0",24)
# print (address,networka,networkb)
# print addressInNetwork(address,networka)
# print addressInNetwork(address,networkb)

def draw_with_uid(uid):
    logging.info("draw: "+uid)
    # data_es = Elasticsearch(hosts='81.91.137.50:9200', timeout=2000, request_timeout=2000)
    data_es = Elasticsearch(hosts='127.0.0.1:9200', timeout=2000, request_timeout=2000)
    if not data_es.indices.exists(index="graph_map"):
        data_es.indices.create(index="graph_map")
    nodes = []
    edges = []
    c = 0
    ip_id = {}
    id_ip = {}
    mask_map = {}
    parent_map = {}
    pranet_count = {}
    mask_list = []
    mask_list_obj = {}
    range_ips = []
    host_id = {}
    f_t = {}
    hosts = []
    route_list = []

    URL = "https://dashboard.netseen.io/api/v1/topology/services/user-ranges?uid="+uid
    logging.info("getting data from: " + URL)
    r = requests.get(url=URL)
    json_data = r.json()
    logging.info("data: " + str(json_data))

    for doc in json_data:
        mask_list.append(doc["ip"]+"/"+str(doc["mask"]))
        mask_list_obj[doc["ip"]+"/"+str(doc["mask"])]=doc
        logging.info("range added for uid: "+uid+" ---- "+doc["ip"]+"/"+str(doc["mask"]))

    s = Search(using=data_es, index="trace_route").query("match", uid=uid)
    for hit in s.scan():
        try:
            route_list.append(hit)
        except:
            logging.info(traceback.format_exc())
    for host in route_list:
        hosts.append(host["ip"])

    # for host in route_list:
    #     for i in range(0, len(host["route"]) - 1):
    #         preip = host["route"][i + 1]["ip"]
    #         ip = host["route"][i]["ip"]
    #         doc = {}
    #         doc["id"] = c
    #         doc["label"] = ip
    #         if not ip in ip_id:
    #             if ip in hosts:
    #                 host_id[ip] = c
    #                 doc["color"] = "#FB7E81"
    #             ip_id[ip] = c
    #             id_ip[c] = ip
    #             nodes.append(doc)
    #             c += 1
    #         doc = {}
    #         doc["id"] = c
    #         doc["label"] = preip
    #         if not preip in ip_id:
    #             if preip in hosts:
    #                 host_id[preip] = c
    #                 doc["color"] = "#FB7E81"
    #             ip_id[preip] = c
    #             id_ip[c] = preip
    #             nodes.append(doc)
    #             c += 1
    #
    #         if i == (len(host["route"]) - 2) and preip in hosts:
    #             parent_map[preip] = ip
    #             find = False
    #             mask_network=""
    #             for x in mask_map:
    #                 if (ipaddress.ip_address(preip) in ipaddress.ip_network(x, False)) and ip == mask_map[x]:
    #                     mask_network=x
    #                     find = True
    #                     break
    #             if not find:
    #                 mask_network=(preip + "/28")
    #                 mask_map[mask_network] = ip
    #                 doc = {}
    #                 doc["id"] = c
    #                 doc["label"] = mask_network
    #                 if not mask_network in ip_id:
    #                     ip_id[mask_network] = c
    #                     id_ip[c] = mask_network
    #                     nodes.append(doc)
    #                     c += 1
    #             else:
    #                 doc = {}
    #                 doc["id"] = c
    #                 doc["label"] = mask_network
    #                 if not mask_network in ip_id:
    #                     ip_id[mask_network] = c
    #                     id_ip[c] = mask_network
    #                     nodes.append(doc)
    #                     c += 1
    #             from_to = {}
    #             from_to["to"] = ip_id[ip]
    #             from_to["from"] = ip_id[mask_network]
    #             ft = str(from_to["from"]) + ":" + str(from_to["to"])
    #             tf = str(from_to["to"]) + ":" + str(from_to["from"])
    #             if not from_to["from"] == from_to["to"]:
    #                 if not ft in f_t and not tf in f_t:
    #                     edges.append(from_to)
    #                     f_t[ft] = ft
    #                     f_t[tf] = tf
    #             from_to = {}
    #             from_to["to"] = ip_id[mask_network]
    #             from_to["from"] = ip_id[preip]
    #             ft = str(from_to["from"]) + ":" + str(from_to["to"])
    #             tf = str(from_to["to"]) + ":" + str(from_to["from"])
    #             if not from_to["from"] == from_to["to"]:
    #                 if not ft in f_t and not tf in f_t:
    #                     edges.append(from_to)
    #                     f_t[ft] = ft
    #                     f_t[tf] = tf
    #         else:
    #             from_to = {}
    #             from_to["from"] = ip_id[preip]
    #             from_to["to"] = ip_id[ip]
    #             ft = str(from_to["from"]) + ":" + str(from_to["to"])
    #             tf = str(from_to["to"]) + ":" + str(from_to["from"])
    #             if not from_to["from"] == from_to["to"]:
    #                 if not ft in f_t and not tf in f_t:
    #                     edges.append(from_to)
    #                     f_t[ft] = ft
    #                     f_t[tf] = tf

    for host in route_list:
        if len(host["route"])<=2:
            continue
        for i in range(0, len(host["route"]) - 1):
            preip = host["route"][i + 1]["ip"]
            # if not preip[0:preip.rfind(".")] in mask_list:
            # doc = {}
            # doc["id"] = c
            # doc["label"] = preip[0:preip.rfind(".")] +".0/24"
            # if not doc["label"] in ip_id:
            #     ip_id[doc["label"]] = c
            #     id_ip[c] = doc["label"]
            #     nodes.append(doc)
            #     c += 1
            # mask_map[preip] = doc["label"]
            # if not doc["label"] in mask_list:
            #     mask_list.append(doc["label"])

            ip = host["route"][i]["ip"]
            # if not ip[0:ip.rfind(".")] in mask_list:
            # doc = {}
            # doc["id"] = c
            # doc["label"] = ip[0:ip.rfind(".")]+".0/24"
            # if not doc["label"] in ip_id:
            #     ip_id[doc["label"]] = c
            #     id_ip[c] = doc["label"]
            #     nodes.append(doc)
            #     c += 1
            # mask_map[ip] = doc["label"]
            # if not doc["label"] in mask_list:
            #     mask_list.append(doc["label"])

            doc = {}
            doc["id"] = c
            doc["label"] = ip
            if not ip in ip_id:
                if ip in hosts:
                    host_id[ip] = c
                    doc["color"] = "#FB7E81"
                ip_id[ip] = c
                id_ip[c] = ip
                nodes.append(doc)
                c += 1
            doc = {}
            doc["id"] = c
            doc["label"] = preip
            if not preip in ip_id:
                if preip in hosts:
                    host_id[preip] = c
                    doc["color"] = "#FB7E81"
                ip_id[preip] = c
                id_ip[c] = preip
                nodes.append(doc)
                c += 1

            # logging.info(str(i)+"   "+str(len(host["route"]) - 2))
            # logging.info(ip+"   "+str(hosts))
            # if i == (len(host["route"]) - 2) and preip in hosts:
            #     logging.info("last host mask added")
            #     from_to = {}
            #     from_to["from"] = ip_id[ip]
            #     from_to["to"] = ip_id[mask_map[preip]]
            #     ft = str(from_to["from"]) + ":" + str(from_to["to"])
            #     tf = str(from_to["to"]) + ":" + str(from_to["from"])
            #     if not from_to["from"] == from_to["to"]:
            #         if not ft in f_t and not tf in f_t:
            #             edges.append(from_to)
            #             f_t[ft] = ft
            #             f_t[tf] = tf
            #     from_to = {}
            #     from_to["from"] = ip_id[mask_map[preip]]
            #     from_to["to"] = ip_id[preip]
            #     ft = str(from_to["from"]) + ":" + str(from_to["to"])
            #     tf = str(from_to["to"]) + ":" + str(from_to["from"])
            #     if not from_to["from"] == from_to["to"]:
            #         if not ft in f_t and not tf in f_t:
            #             edges.append(from_to)
            #             f_t[ft] = ft
            #             f_t[tf] = tf
            # else:
            #     from_to = {}
            #     from_to["from"] = ip_id[preip]
            #     from_to["to"] = ip_id[ip]
            #     ft = str(from_to["from"]) + ":" + str(from_to["to"])
            #     tf = str(from_to["to"]) + ":" + str(from_to["from"])
            #     if not from_to["from"] == from_to["to"]:
            #         if not ft in f_t and not tf in f_t:
            #             edges.append(from_to)
            #             f_t[ft] = ft
            #             f_t[tf] = tf

            # ----------------------------------------
            # from_to = {}
            # from_to["to"] = ip_id[preip]
            # from_to["from"] = ip_id[ip]
            # ft = str(from_to["from"]) + ":" + str(from_to["to"])
            # tf = str(from_to["to"]) + ":" + str(from_to["from"])
            # if not from_to["from"] == from_to["to"]:
            #     if not ft in f_t and not tf in f_t:
            #         edges.append(from_to)
            #         f_t[ft] = ft
            #         f_t[tf] = tf
            # ----------------------------------------

            if i == (len(host["route"]) - 2) and preip in hosts:
                parent_map[preip] = ip
                find = False
                # mask_network=""
                for x in mask_map:
                    if (ipaddress.ip_address(preip) in ipaddress.ip_network(x, False)) and ip == mask_map[x]:
                        # mask_network=x
                        find = True
                        break
                if not find:
                    mask_network=(preip + "/28")
                    mask_map[mask_network] = ip
                #     doc = {}
                #     doc["id"] = c
                #     doc["label"] = mask_network
                #     if not mask_network in ip_id:
                #         ip_id[mask_network] = c
                #         id_ip[c] = mask_network
                #         nodes.append(doc)
                #         c += 1
                # else:
                #     doc = {}
                #     doc["id"] = c
                #     doc["label"] = mask_network
                #     if not mask_network in ip_id:
                #         ip_id[mask_network] = c
                #         id_ip[c] = mask_network
                #         nodes.append(doc)
                #         c += 1
                # logging.info("last host mask added")
                # from_to = {}
                # from_to["to"] = ip_id[ip]
                # from_to["from"] = ip_id[mask_network]
                # ft = str(from_to["from"]) + ":" + str(from_to["to"])
                # tf = str(from_to["to"]) + ":" + str(from_to["from"])
                # if not from_to["from"] == from_to["to"]:
                #     if not ft in f_t and not tf in f_t:
                #         edges.append(from_to)
                #         f_t[ft] = ft
                #         f_t[tf] = tf
                # from_to = {}
                # from_to["to"] = ip_id[mask_network]
                # from_to["from"] = ip_id[preip]
                # ft = str(from_to["from"]) + ":" + str(from_to["to"])
                # tf = str(from_to["to"]) + ":" + str(from_to["from"])
                # if not from_to["from"] == from_to["to"]:
                #     if not ft in f_t and not tf in f_t:
                #         edges.append(from_to)
                #         f_t[ft] = ft
                #         f_t[tf] = tf
            # else:
            from_to = {}
            from_to["from"] = ip_id[preip]
            from_to["to"] = ip_id[ip]
            ft = str(from_to["from"]) + ":" + str(from_to["to"])
            tf = str(from_to["to"]) + ":" + str(from_to["from"])
            if not from_to["from"] == from_to["to"]:
                if not ft in f_t and not tf in f_t:
                    edges.append(from_to)
                    f_t[ft] = ft
                    f_t[tf] = tf
            #
            # if i == len(host["route"]) - 2:
            #     parent_map[id_ip[from_to["to"]]]=id_ip[from_to["from"]]
            #     find = False
            #     for x in mask_map:
            #         if (ipaddress.ip_address(id_ip[from_to["to"]]) in ipaddress.ip_network(x, False)) and id_ip[from_to["from"]] != mask_map[x]:
            #             find=True
            #             break
            #     if not find:
            #         mask_map[id_ip[from_to["to"]] +"/28"]=id_ip[from_to["from"]]


    host_list = []
    for host in host_id:
        host_list.append(host_id[host])
    # logging.info("nodes: "+str(nodes))
    # logging.info("edges: "+str(edges))
    # logging.info("host list: "+str(host_list))
    rm_nodes = []
    temp_edges = []
    for i in range(0, len(nodes)):
        if nodes[i]["label"] in host_list:
            continue
        rm_nodes.append(nodes[i]["id"])
        g2 = dfs.Graph(len(nodes))
        temp_edges = []
        for edge in edges:
            if not (edge["from"] in rm_nodes or edge["to"] in rm_nodes):
                g2.addEdge(edge["from"], edge["to"])
                temp_edges.append(edge)
        cc = g2.connectedComponents()
        # print(cc)
        find = False
        for ccc in cc:
            if set(host_list).issubset(ccc):
                # print(ccc)
                find = True
                break
        if not find:
            rm_nodes.pop()

    g2 = dfs.Graph(len(nodes))
    temp_edges = []
    for edge in edges:
        if not (edge["from"] in rm_nodes or edge["to"] in rm_nodes):
            g2.addEdge(edge["from"], edge["to"])
            temp_edges.append(edge)
    cc = g2.connectedComponents()
    # logging.info("partions graph: "+str(cc))
    # logging.info("1633: "+str(nodes[1633]))
    # logging.info("1634: "+str(nodes[1634]))
    fix_edge_list = []
    fix_node_list = []
    fix_node_map = {}

    for ccc in cc:
        logging.info(host_list)
        logging.info(ccc)
        if set(host_list).issubset(ccc):
            for i in range(0, len(ccc)):
                doc = {}
                doc["id"] = i
                doc["label"] = id_ip[ccc[i]]
                if id_ip[ccc[i]] in hosts:
                    doc["color"] = "#FB7E81"
                    for qwe in mask_list:
                        if ipaddress.ip_address(id_ip[ccc[i]]) in ipaddress.ip_network(qwe,False):
                            doc["parent"] = qwe
                            doc["label_name"]=mask_list_obj[qwe]["label"]
                            break
                    for qwe in mask_map:
                        if ipaddress.ip_address(id_ip[ccc[i]]) in ipaddress.ip_network(qwe,False):
                            doc["cluster"] = qwe
                            break
                fix_node_list.append(doc)
                fix_node_map[ccc[i]] = i
            for edge in temp_edges:
                from_to = {}
                from_to["from"] = fix_node_map[edge["from"]]
                from_to["to"] = fix_node_map[edge["to"]]
                fix_edge_list.append(from_to)
            break
    # logging.info(cc)
    # logging.info(fix_node_list)
    # logging.info(fix_edge_list)
    doc = {}
    doc["nodes"] = fix_node_list
    doc["edges"] = fix_edge_list
    doc["uid"] = uid
    doc["update_time"] = time.time()

    s = Search(using=data_es, index="graph_map").query("match", uid=uid)

    hit_list = []
    for hit in s.scan():
        try:
            hit_list.append(hit)
        except:
            logging.info(traceback.format_exc())

    # response = s.execute()
    if len(hit_list) != 0:
        logging.info("exist uid: " + uid + " --- updating graph ...")
        data_es.update("graph_map", id=hit_list[0].meta.id,  body={"doc":doc})
    else:
        logging.info("new uid: " + uid + " --- inserting graph ...")
        data_es.index("graph_map", body=doc)

    web_txt = ""
    with open("web_ex_fixed.html") as fr:
        for line in fr.readlines():
            web_txt += line
    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        fix_node_list) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        fix_edge_list) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open(uid + "_web_ex_partitioning.html", "w") as w:
        w.write(web_txt)

    # web_txt = ""
    # with open("D:/PycharmProjects/topology_detectionx/web_ex_fixed.html") as fr:
    #     for line in fr.readlines():
    #         web_txt += line
    # parts = web_txt.split("//nnnooodddeeesss")
    # web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
    #     fix_node_list) + ");\n" + "//nnnooodddeeesss" + parts[2]
    # parts = web_txt.split("//eeedddgggeeesss")
    # web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
    #     fix_edge_list) + ");\n" + "//eeedddgggeeesss" + parts[2]
    #
    # with open("D:/PycharmProjects/topology_detectionx/"+uid + "_web_ex_partitioning.html", "w") as w:
    #     w.write(web_txt)
