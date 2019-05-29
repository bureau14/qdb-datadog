# -*- coding: utf-8 -*-

import argparse
import quasardb
import requests

import json
from functools import reduce
from .metrics import key_to_metric
from .metrics import MetricType

def get_args():
    parser = argparse.ArgumentParser(
        description=(
            'Fetch QuasarDB metrics for local node and export to CloudWatch.'))
    parser.add_argument(
        '--cluster',
        dest='cluster_uri',
        help='QuasarDB cluster uri to connect to. Defaults to qdb://127.0.0.1:2836',
        default="qdb://127.0.0.1:2836")

    parser.add_argument(
        '--cluster-public-key',
        dest='cluster_public_key',
        help='Cluster public key file')

    parser.add_argument(
        '--user-security-file',
        dest='user_security_file',
        help='User security file, containing both username and private access token.')

    parser.add_argument(
        '--node-id',
        dest='node_id',
        help='Node id to collect metrics from, e.g. 0-0-0-1')


    parser.add_argument(
        '--prefix',
        dest='prefix',
        help='Prefix to add to all metrics')



    return parser.parse_args()

def _parse_user_security_file(x):
    with open(x, 'r') as fp:
        parsed = json.load(fp)
        return (parsed['username'], parsed['secret_key'])

def _slurp(x):
    with open(x, 'r') as fp:
        return fp.read()

def get_qdb_conn(uri, cluster_public_key=None, user_security_file=None):
    if cluster_public_key and user_security_file:
        user, private_key = _parse_user_security_file(user_security_file)
        public_key = _slurp(cluster_public_key)
        return quasardb.Cluster(uri,
                                user_name=user,
                                user_private_key=private_key,
                                cluster_public_key=public_key)
    else:
        return quasardb.Cluster(uri)

def parse_key(key):
    return key.split('.', 3)[-1]

def collect_keys(conn, node_id):
    return conn.prefix_get(str('$qdb.statistics.' + node_id), 200)

def collect_metric(conn, metric_type, key):

    if metric_type is None:
        return None

    fn = metric_type.lookup_fn(conn)
    return fn(key).get()

def collect_metrics(conn, keys):
    res = dict()

    for key in keys:
        # $qdb.statistics.<node_id>.foo.bar -> foo.bar
        parsed = parse_key(key)
        metric = key_to_metric(parsed)

        if metric is not None and metric['type'].value is not MetricType.STRING.value:
            val = collect_metric(conn, metric['type'], key)
            if 'parser' in metric:
                val = metric['parser'](val)

            metric['value'] = val

            res[parsed] = metric

    return res

def _chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]

def print_metrics(metrics, prefix=None, instance_id=None):
    xs = []
    for k in metrics:
        v = metrics[k]

        t = None
        if v['type'] is MetricType.STRING:
            t = 'STRING'
        elif v['type'] is MetricType.GAUGE:
            t = 'GAUGE'
        elif v['type'] is MetricType.COUNTER:
            t = 'COUNTER'

        if prefix:
            k = prefix + '.' + k

        print(k + "," + t +"," + str(v['value']))

    return True

def main():
    args = get_args()

    conn = get_qdb_conn(args.cluster_uri,
                        cluster_public_key=args.cluster_public_key,
                        user_security_file=args.user_security_file)
    keys = collect_keys(conn, args.node_id)
    metrics = collect_metrics(conn, keys)

    result = print_metrics(metrics, prefix=args.prefix)

    return result
