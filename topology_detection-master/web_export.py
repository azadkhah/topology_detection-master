import json
import logging
import random

import dfs
import new_g


def create_web():
    web_txt = ""
    with open("web_exports/web_ex.html") as fr:
        for line in fr.readlines():
            web_txt += line
    ip_id = {}
    nodes = []
    edges = []
    try:
        c = 1
        with open("files/g_map.json") as wr:
            route_map = json.load(wr)
            for node_1 in route_map:
                doc = {}
                doc["id"] = c
                doc["label"] = node_1
                if not node_1 in ip_id:
                    ip_id[node_1] = c
                    nodes.append(doc)
                c += 1
                for node_2 in route_map[node_1]:
                    doc = {}
                    doc["id"] = c
                    doc["label"] = node_2
                    if not node_2 in ip_id:
                        ip_id[node_2] = c
                        nodes.append(doc)
                    c += 1
            for node_1 in route_map:
                for node_2 in route_map[node_1]:
                    from_to = {}
                    from_to["from"] = ip_id[node_1]
                    from_to["to"] = ip_id[node_2]
                    if not from_to["from"] == from_to["to"]:
                        edges.append(from_to)
        print(json.dumps(nodes))
        print(json.dumps(edges))
        # print(edges)
    except:
        pass

    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        nodes) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        edges) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open("web_exports/web_ex.html", "w") as w:
        w.write(web_txt)


def create_web_limit():
    web_txt = ""
    with open("web_exports/web_ex_limit.html") as fr:
        for line in fr.readlines():
            web_txt += line
    ip_id = {}
    nodes = []
    edges = []
    hosts = []
    with open("files/host_list.txt") as hosts_file:
        for line in hosts_file.readlines():
            hosts.append(line.strip())
    try:
        c = 1
        with open("files/g_map_limit.json") as wr:
            route_map = json.load(wr)
            for node_1 in route_map:
                doc = {}
                doc["id"] = c
                doc["label"] = node_1
                if node_1 in hosts:
                    doc["color"] = "#FB7E81"
                if not node_1 in ip_id:
                    ip_id[node_1] = c
                    nodes.append(doc)
                    c += 1
                for node_2 in route_map[node_1]:
                    doc = {}
                    doc["id"] = c
                    doc["label"] = node_2
                    if node_2 in hosts:
                        doc["color"] = "#FB7E81"
                    if not node_2 in ip_id:
                        ip_id[node_2] = c
                        nodes.append(doc)
                        c += 1
            for node_1 in route_map:
                for node_2 in route_map[node_1]:
                    from_to = {}
                    from_to["from"] = ip_id[node_1]
                    from_to["to"] = ip_id[node_2]
                    from_to["color"] = "#6E6EFD"
                    from_to["value"] = random.randint(1, 10)
                    if not from_to["from"] == from_to["to"]:
                        edges.append(from_to)
        # print(json.dumps(nodes))
        # print(json.dumps(edges))
        # print(edges)
    except:
        pass

    parts = web_txt.split("//nnnooodddeeesss")
    web_txt = parts[0] + "//nnnooodddeeesss\n" + "var nodes = new vis.DataSet(" + json.dumps(
        nodes) + ");\n" + "//nnnooodddeeesss" + parts[2]
    parts = web_txt.split("//eeedddgggeeesss")
    web_txt = parts[0] + "//eeedddgggeeesss\n" + "var edges = new vis.DataSet(" + json.dumps(
        edges) + ");\n" + "//eeedddgggeeesss" + parts[2]

    with open("web_exports/web_ex_limit.html", "w") as w:
        w.write(web_txt)



    # logging.info(len(nodes))
    g1 = new_g.Graph(len(nodes))
    g2 = dfs.Graph(len(nodes))
    for edge in edges:
        # print(edge)
        g1.addEdge(edge["from"]-1, edge["to"]-1)
        g2.addEdge(edge["from"]-1, edge["to"]-1)
        # g1.addEdge(edge["to"], edge["from"])
    isConnected = True
    for i in range(0, len(hosts)):
        for j in range(i + 1, len(hosts)):
            if not g1.isReachable(ip_id[hosts[i]]-1, ip_id[hosts[j]]-1):
                isConnected = False
                break
    cc=g2.connectedComponents()
    # logging.info(isConnected)
    # logging.info(cc)
    return cc
    # print(g1.graph)
    # print(g1.isSC())
# if __name__ == '__main__':
#     create_web()
