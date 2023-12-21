import copy
import json
import logging

import networkx as nx
import matplotlib.pyplot as plt

import dfs
from web_export import create_web_limit


def route_it():
    route_map = {}
    route_list_map = {}
    try:
        with open("files/route_list_cp.json") as wr:
            route_list_map = json.load(wr)
    except:
        pass

    x = 100000
    for host in route_list_map:
        logging.info("tracing: " + host.strip())
        c = len(route_list_map[host])
        c *= -1
        if c < x:
            x = c
        for i in range(-1, c, -1):
            preip = route_list_map[host][i - 1]
            ip = route_list_map[host][i]
            logging.info(preip)
            if not ip in route_map:
                route_map[ip] = {}
            if not preip in route_map:
                route_map[preip] = {}
            route_map[preip][ip] = i
        logging.info("---------------------------------------------")

    G = nx.Graph()
    for node_1 in route_map:
        for node_2 in route_map[node_1]:
            G.add_edge(node_1, node_2)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.savefig("map_from_file.png")
    # plt.show()

    with open("files/g_map_limit.json", 'w') as wr:
        json.dump(route_map, wr)

    # logging.info("wtf")
    cc = create_web_limit()
    rmc = copy.deepcopy(route_map)
    for i in range(x, -1):
        for j in route_map:
            for k in route_map[j]:
                # logging.info("x: "+str(route_map[j][k]))
                if route_map[j][k] == i:
                    del rmc[j][k]
                    with open("files/g_map_limit.json", 'w') as wr:
                        json.dump(rmc, wr)
                    cc = create_web_limit()
                    logging.info(cc)
                    if len(cc) >= 2:
                        rmc[j][k] = x

    with open("files/g_map_limit.json", 'w') as wr:
        json.dump(rmc, wr)
    create_web_limit()


def route_it_fixed():
    acc_name = "netbee"
    route_map = {}
    route_list_map = {}
    max_distance = {}
    try:
        with open(acc_name + "_route_list.json") as wr:
            route_list_map = json.load(wr)
    except:
        pass
    try:
        with open(acc_name + "_max_distance.json") as wr:
            max_distance = json.load(wr)
    except:
        pass
    web_txt = ""
    with open("web_exports/web_ex_fixed.html") as fr:
        for line in fr.readlines():
            web_txt += line
    ip_id = {}
    f_t = {}
    nodes = []
    edges = []
    hosts = []
    with open(acc_name + ".txt") as hosts_file:
        for line in hosts_file.readlines():
            hosts.append(line.strip())

    layer = -1
    c = 1
    xl = 0
    while True:
        for host in route_list_map:
            logging.info("tracing: " + host.strip())
            preip = route_list_map[host][layer - 1]["ip"]
            ip = route_list_map[host][layer]["ip"]
            diff = route_list_map[host][layer]["ttl"] - route_list_map[host][layer - 1]["ttl"]
            doc = {}
            doc["id"] = c
            doc["label"] = ip
            doc["level"] = max_distance[ip]
            if ip in hosts:
                doc["color"] = "#FB7E81"
            if not ip in ip_id:
                ip_id[ip] = c
                nodes.append(doc)
                c += 1
            doc = {}
            doc["id"] = c
            doc["label"] = preip
            doc["level"] = max_distance[preip]
            if preip in hosts:
                doc["color"] = "#FB7E81"
            if not preip in ip_id:
                ip_id[preip] = c
                nodes.append(doc)
                c += 1
            from_to = {}
            from_to["from"] = ip_id[preip]
            from_to["to"] = ip_id[ip]
            ft = str(from_to["from"]) + ":" + str(from_to["to"])
            tf = str(from_to["to"]) + ":" + str(from_to["from"])
            # from_to["color"] = "#6E6EFD"
            if not ip in hosts and not preip in hosts:
                from_to["value"] = diff
                from_to["label"] = str(diff)
            if not from_to["from"] == from_to["to"]:
                if not ft in f_t and not tf in f_t:
                    edges.append(from_to)
                    f_t[ft] = ft
                    f_t[tf] = tf
        layer -= 1
        if layer == -4:
            break
        xl += 1
        g2 = dfs.Graph(len(nodes))
        for edge in edges:
            g2.addEdge(edge["from"] - 1, edge["to"] - 1)
        cc = g2.connectedComponents()
        print(cc)
        if len(cc) == 1:
            break

    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        nodes) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        edges) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open(acc_name + "_web_ex.html", "w") as w:
        w.write(web_txt)


def route_with_distance():
    acc_name = "netbee"
    route_map = {}
    route_list_map = {}
    max_distance = {}
    try:
        with open(acc_name + "_route_list.json") as wr:
            route_list_map = json.load(wr)
    except:
        pass
    try:
        with open(acc_name + "_max_distance.json") as wr:
            max_distance = json.load(wr)
    except:
        pass
    web_txt = ""
    with open("web_exports/web_ex_fixed.html") as fr:
        for line in fr.readlines():
            web_txt += line

    hosts = []
    with open(acc_name + ".txt") as hosts_file:
        for line in hosts_file.readlines():
            hosts.append(line.strip())

    # layer = -1
    # xl = 0
    dist = 0
    dist_part = {}
    ip_id = {}
    c = 1
    d_nodes = {}
    f_t = {}
    nodes = []
    edges = []
    while True:


        for host in max_distance:
            if max_distance[host] <= dist:
                d_nodes[host] = max_distance[host]

        for host in route_list_map:
            # logging.info("tracing: " + host.strip())
            for i in range(0, len(route_list_map[host]) - 1):
                preip = route_list_map[host][i + 1]["ip"]
                ip = route_list_map[host][i]["ip"]
                diff = route_list_map[host][i + 1]["ttl"] - route_list_map[host][i]["ttl"]
                if ip in d_nodes:
                    doc = {}
                    doc["id"] = c
                    doc["label"] = ip
                    doc["level"] = max_distance[ip]
                    if ip in hosts:
                        doc["color"] = "#FB7E81"
                    if not ip in ip_id:
                        ip_id[ip] = c
                        nodes.append(doc)
                        c += 1
                if preip in d_nodes:
                    doc = {}
                    doc["id"] = c
                    doc["label"] = preip
                    doc["level"] = max_distance[preip]
                    if preip in hosts:
                        doc["color"] = "#FB7E81"
                    if not preip in ip_id:
                        ip_id[preip] = c
                        nodes.append(doc)
                        c += 1
                if ip in d_nodes and preip in d_nodes:
                    from_to = {}
                    from_to["from"] = ip_id[preip]
                    from_to["to"] = ip_id[ip]
                    ft = str(from_to["from"]) + ":" + str(from_to["to"])
                    tf = str(from_to["to"]) + ":" + str(from_to["from"])
                    # from_to["color"] = "#6E6EFD"
                    if not ip in hosts and not preip in hosts:
                        from_to["value"] = diff
                        from_to["label"] = str(diff)
                    if not from_to["from"] == from_to["to"]:
                        if not ft in f_t and not tf in f_t:
                            edges.append(from_to)
                            f_t[ft] = ft
                            f_t[tf] = tf
        # layer -= 1
        # if layer == -4:
        #     break
        # xl += 1
        # logging.info(nodes)
        # logging.info(edges)
        g2 = dfs.Graph(len(nodes))
        for edge in edges:
            g2.addEdge(edge["from"] - 1, edge["to"] - 1)
        cc = g2.connectedComponents()
        logging.info(cc)
        dist_part[dist]=len(cc)
        # logging.info(len(cc))
        if len(cc) == 2:
            break
        dist += 1

    while True:

        for i in range(0,len(nodes)):
            cp_nodes=copy.deepcopy(nodes)
            logging.info(cp_nodes)
            logging.info(nodes)
            cp_edges= []
            logging.info("remove: "+str(cp_nodes[i]))
            # cp_nodes.remove(i)
            del cp_nodes[i]
            for cp_node in cp_nodes:
                if cp_node['id']>nodes[i]['id']:
                    logging.info(cp_node['label']+": "+str(cp_node['id'])+" -> "+str(cp_node['id']-1))
                    cp_node['id']-=1
            for edge in edges:
                if edge['from'] == nodes[i]['id'] or edge['to'] == nodes[i]['id']:
                    continue
                from_n=0
                to_n=0
                if edge['from']>nodes[i]['id']:
                    from_n=edge['from']-1
                if edge['to']>nodes[i]['id']:
                    to_n=edge['to']-1
                from_to = {}
                from_to["from"] = from_n
                from_to["to"] = to_n
                if "value" in edge:
                    from_to["value"] = edge['value']
                if "label" in edge:
                    from_to["label"] = edge['label']
                cp_edges.append(from_to)
            logging.info(cp_nodes)
            logging.info(cp_edges)
            g2 = dfs.Graph(len(cp_nodes))
            for edge in cp_edges:
                g2.addEdge(edge["from"] - 1, edge["to"] - 1)
            cc = g2.connectedComponents()
            logging.info(cc)

    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        nodes) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        edges) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open(acc_name + "_web_ex_dist.html", "w") as w:
        w.write(web_txt)


def fixed_partitioning():
    acc_name = "afranet"
    route_map = {}
    route_list_map = {}
    max_distance = {}
    ip_id = {}
    host_id = {}
    f_t={}
    hosts = []
    nodes = []
    edges = []
    try:
        with open(acc_name + "_route_list.json") as wr:
            route_list_map = json.load(wr)
    except:
        pass
    try:
        with open(acc_name + "_max_distance.json") as wr:
            max_distance = json.load(wr)
    except:
        pass
    with open(acc_name + ".txt") as hosts_file:
        for line in hosts_file.readlines():
            hosts.append(line.strip())

    c = 0
    # while True:
    for host in route_list_map:
        for i in range(0, len(route_list_map[host]) - 1):
            preip = route_list_map[host][i + 1]["ip"]
            ip = route_list_map[host][i]["ip"]
            diff = route_list_map[host][i+1]["ttl"] - route_list_map[host][i]["ttl"]
            doc = {}
            doc["id"] = c
            doc["label"] = ip
            doc["level"] = max_distance[ip]
            if not ip in ip_id:
                if ip in hosts:
                    host_id[ip] = c
                    doc["color"] = "#FB7E81"
                ip_id[ip] = c
                nodes.append(doc)
                c += 1
            doc = {}
            doc["id"] = c
            doc["label"] = preip
            doc["level"] = max_distance[preip]
            if not preip in ip_id:
                if preip in hosts:
                    host_id[preip] = c
                    doc["color"] = "#FB7E81"
                ip_id[preip] = c
                nodes.append(doc)
                c += 1
            from_to = {}
            from_to["from"] = ip_id[preip]
            from_to["to"] = ip_id[ip]
            ft = str(from_to["from"]) + ":" + str(from_to["to"])
            tf = str(from_to["to"]) + ":" + str(from_to["from"])
            # from_to["color"] = "#6E6EFD"
            if not ip in hosts and not preip in hosts:
                from_to["value"] = diff
                from_to["label"] = str(diff)
            if not from_to["from"] == from_to["to"]:
                if not ft in f_t and not tf in f_t:
                    edges.append(from_to)
                    f_t[ft] = ft
                    f_t[tf] = tf
    g2 = dfs.Graph(len(nodes))
    for edge in edges:
        g2.addEdge(edge["from"], edge["to"])
    cc = g2.connectedComponents()
    logging.info(cc)

    host_list=[]
    for host in host_id:
        host_list.append(host_id[host])
    print("host lists: "+str(host_list))
    rm_nodes=[]
    temp_edges=[]
    for i in range(0,len(nodes)):
        rm_nodes.append(nodes[i]["id"])
        g2 = dfs.Graph(len(nodes))
        temp_edges=[]
        for edge in edges:
            if not (edge["from"] in rm_nodes or edge["to"] in rm_nodes):
                g2.addEdge(edge["from"], edge["to"])
                temp_edges.append(edge)
        cc = g2.connectedComponents()
        # print(cc)
        find=False
        for ccc in cc:
            if set(host_list).issubset(ccc):
                print(ccc)
                find=True
                break
        if not find:
            rm_nodes.pop()

    temp_edges=[]
    for edge in edges:
        if not (edge["from"] in rm_nodes or edge["to"] in rm_nodes):
            g2.addEdge(edge["from"], edge["to"])
            temp_edges.append(edge)
    cc = g2.connectedComponents()

    web_txt = ""
    with open("web_exports/web_ex_fixed.html") as fr:
        for line in fr.readlines():
            web_txt += line
    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        nodes) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        temp_edges) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open(acc_name + "_web_ex_partitioning.html", "w") as w:
        w.write(web_txt)
