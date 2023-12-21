import logging
import sys

import draw_topology
import rebuild_graphs
import route_map_from_file
import trace_proccess_maker
from route_map_from_file import route_it, route_it_fixed, route_with_distance

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
main_logger.addHandler(handler)

from threading import Thread

import flask
from flask import send_file, request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True
# app.config["PORT"] = 8000


#
# main_logger = logging.getLogger()
# main_logger.setLevel(logging.INFO)
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# main_logger.addHandler(handler)


@app.route('/trace', methods=['GET'])
def trace_version():
    all_args = request.args.to_dict()
    thread1 = Thread(target=trace_proccess_maker.p_maker, args=(all_args['v'], 10,))
    thread1.start()
    return jsonify(all_args)


@app.route('/graph', methods=['GET'])
def draw_graph():
    all_args = request.args.to_dict()
    thread1 = Thread(target=draw_topology.draw_with_uid, args=(all_args['uid'],))
    thread1.start()
    print(all_args)
    return jsonify(all_args)

@app.route('/rebuild-graphs', methods=['GET'])
def rebuild_all():
    thread1 = Thread(target=rebuild_graphs.rebuild, args=())
    thread1.start()
    return jsonify("rebuild graphs")


@app.route('/pre-checker', methods=['GET'])
def pre_checker():
    all_args = request.args.to_dict()
    thread1 = Thread(target=trace_proccess_maker.pre_version_checker, args=(int(all_args['from']), int(all_args['to']), int(all_args['th']),))
    thread1.start()
    print(all_args)
    return jsonify(all_args)


# @app.route('/exit-addresses', methods=['GET'])
# def home():
#     return send_file("exit-addresses.txt")

app.run(host="0.0.0.0")
