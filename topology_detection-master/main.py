import re
import logging
import sys
from subprocess import Popen, PIPE
import json
import platform
import networkx as nx
import matplotlib.pyplot as plt

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
main_logger.addHandler(handler)

route_map = {}
max_distance = {}

if __name__ == '__main__':

    acc_name = "afranet"

    try:
        with open(acc_name + "_g_map.json") as wr:
            route_map = json.load(wr)
            G = nx.Graph()
            for node_1 in route_map:
                for node_2 in route_map[node_1]:
                    G.add_edge(node_1, node_2)
            nx.draw(G, with_labels=True, font_weight='bold')
            plt.savefig(acc_name + "_test.png")
            plt.show()
    except:
        pass

    with open(acc_name + ".txt") as f:
        route_list_map = {}
        for host in f.readlines():
            route_list = []
            temp_max_distance = {}
            logging.info("tracing: " + host.strip())
            c = 0
            c2 = 0
            max_c2 = 0
            count = 0
            logging.info("platform: " + str(platform.platform()))
            p = None
            if "windows" in platform.platform().strip().lower():
                p = Popen(['tracert', host.strip()], stdout=PIPE)
            elif "linux" in platform.platform().strip().lower():
                p = Popen(['traceroute', host.strip()], stdout=PIPE)
            preip = None
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
                    logging.info(ip.group())
                    if (c == 1 and host.strip() == ip.group()) or ip.group().startswith("192.168"):
                        logging.info("first node or local router skipping: " + ip.group())
                        continue
                    if not ip.group() in temp_max_distance:
                        temp_max_distance[ip.group()] = c2
                    else:
                        if c2 > temp_max_distance[ip.group()]:
                            temp_max_distance[ip.group()] = c2
                    if c2>max_c2:
                        max_c2=c2
                    c2 += 1
                    route_list.append({"ip": ip.group(), "ttl": count})
                    if ip.group().__eq__(host.strip()):
                        break
                    if not ip.group() in route_map:
                        route_map[ip.group()] = {}
                    if preip:
                        if not preip.group() in route_map:
                            route_map[preip.group()] = {}
                        route_map[preip.group()][ip.group()] = 1
                    preip = ip

            if preip and not preip.group() == host.strip():
                route_map[preip.group()][host.strip()] = 1
            if not route_list[-1]["ip"].__eq__(host.strip()):
                route_list.append({"ip": host.strip(), "ttl": count})
            route_list_map[host.strip()] = route_list

            if not host.strip() in temp_max_distance:
                max_c2+=1
                temp_max_distance[host.strip()]=max_c2
            for ip in temp_max_distance:
                temp_max_distance[ip]=max_c2-temp_max_distance[ip]
                if not ip in max_distance:
                    max_distance[ip] = temp_max_distance[ip]
                else:
                    if temp_max_distance[ip] > max_distance[ip]:
                        max_distance[ip] = temp_max_distance[ip]
            logging.info("---------------------------------------------")
        logging.info(route_map)
        # G = nx.Graph()
        # for node_1 in route_map:
        #     for node_2 in route_map[node_1]:
        #         G.add_edge(node_1, node_2)
        # nx.draw(G, with_labels=True, font_weight='bold')
        # plt.savefig("path_graph3.png")
        # plt.show()
        # G = nx.Graph()
        # for host in route_list_map:
        #     for i in range(-1, -6, -1):
        #         G.add_edge(route_list_map[host][i], route_list_map[host][i - 1])
        # nx.draw(G, with_labels=True, font_weight='bold')
        # plt.savefig("path_graph.png")
        # plt.show()
        with open(acc_name + "_max_distance.json", 'w') as wr:
            json.dump(max_distance, wr)
        with open(acc_name + "_g_map.json", 'w') as wr:
            json.dump(route_map, wr)
        with open(acc_name + "_route_list.json", 'w') as wr:
            json.dump(route_list_map, wr)
    # webb.traceroute("217.218.111.39")
    # target = ["217.218.111.39"]
    # result, unans = traceroute(target,l4=UDP(sport=RandShort())/DNS(qd=DNSQR(qname="www.google.com")))
    # print(result)
    # print(unans)

#
# web_txt=""
# parts=web_txt.split("//nooodddsss")
# web_txt=parts[0]+"//nooodddsss"+"var nodes = new vis.DataSet("+json.dump()+");"+parts[2]+"//nooodddsss"
# parts=web_txt.split("//eeedddgggeeesss")
# web_txt=parts[0]+"//eeedddgggeeesss"+"var edges = new vis.DataSet("+json.dump()+");"+parts[2]+"//eeedddgggeeesss"
