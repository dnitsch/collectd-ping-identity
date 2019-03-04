'''
Ping Identity collectd plugin written in Python.
Collects metrics from heart beat endpoint for Ping Access and Ping Federate and dispatches them to collectd process
'''
# Logging func taken from https://github.com/mleinart/collectd-haproxy

import collectd
import requests, json
import urllib3
from Carbon.Aliases import false
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NAME = 'ping_identity'
VERBOSE_LOGGING = True
DEFAULT_HEARTBEAT_URL = 'https://127.0.0.1:9000/pa/heartbeat.ping'
DEFAULT_INSTANCE = 'engine'
DEFAULT_PRODUCT = 'access'
CONFIGS = []
METRIC_TYPES = {
  'cpu.load': ('cpu_load', 'gauge'),
  'total.jvm.memory': ('jvm_total_memory', 'gauge'),
  'free.jvm.memory': ('jvm_free_memory', 'gauge'),
  'used.jvm.memory': ('jvm_used_memory', 'gauge'),
  'total.physical.system.memory': ('device_total_memory', 'gauge'),
  'total.free.system.memory': ('device_free_memory', 'gauge'),
  'total.used.system.memory': ('device_used_memory', 'gauge'),
  'number.of.cpus': ('total_cores', 'gauge'),
  'open.client.connections': ('current_open_connections', 'gauge'),
  'number.of.applications': ('number_of_applications', 'gauge'),
  'number.of.virtual.hosts': ('number_of_virtual_hosts', 'gauge'),
  'response.concurrency.statistics.mean': ('response_concurrency_statistics_mean', 'gauge'),
  'response.time.statistics.mean': ('response_time_statistics_mean', 'gauge'),
  'response.time.statistics.90.percentile': ('response_tim_statistics_90_percentile', 'gauge')
}

METRIC_NA = {
    'N/A': ('0.00')
}

HEADER = {
        'Accept': "Content-Type,Authorization,Cache-Control",
        'Content-Type': "application/json",
        'X-Xsrf-Header': "PingIdentity",
        'Cache-Control': "no-cache"
}


def configure_callback(conf):
    # global CONFIGS ### HEARTBEAT_URL
    # CONFIGS = []
    VERBOSE_LOGGING = False

    for node in conf.children:
        if node.key == "url":
            heartbeat_url = node.values[0]
        elif node.key == "type":
            instance_type = node.values[0]
        elif node.key == "product":
            product_type = node.values[0]
        else:
            logger('warn', 'Unknown config key: %s' % node.key)

    CONFIGS.append({
        'url': heartbeat_url,
        'type': instance_type,
        'product': product_type
    })

def get_stats(conf):
    _conf = conf
    stats = dict()
    # logger('info', "HEARTBEAT_URL: %s" % HEARTBEAT_URL )
    try:
        r = requests.request('GET', _conf['url'], headers=HEADER, verify=False)
        stats = json.loads(r.content)
    except Exception as e:
        logger('warn', "Unable to retrieve stats: %s" % e.message)
        return stats

    return stats["items"]


def read_callback():
    logger('verb', "beginning read_callback")

    logger('verb', "count configs %s" %  len(CONFIGS))

    for conf in CONFIGS:
        info = get_stats(conf)
        # logger('verb', "info %s" % json.dumps(info))

        if not info:
            logger('warn', "%s: No data received" % NAME)
            return

        for collectd_data in info:
            for key, value in collectd_data.items():
                if key in METRIC_TYPES:
                    key_root, val_type = METRIC_TYPES[key]
                    clean_value = '0.00' if value.split(' ')[0] == 'N/A' else  value.split(' ')[0]
                    logger('verb', "value %s" % value.split(' ')[0] )
                    logger('verb', "type_instance %s" % conf['type'] + "." + key_root )
                    logger('verb', "plugin %s" % NAME )
                    logger('verb', "plugin_instance %s" % "ping-" + conf['product'] )
                    logger('verb', "type %s" % val_type )
                    val = collectd.Values(plugin=NAME, type=val_type, plugin_instance="ping-" + conf['product'])
                    val.type_instance = conf['type'] + "." + key_root
                    val.values = [ clean_value ]
                    val.dispatch()


def logger(t, msg):
    if t == 'err':
        collectd.error('%s: %s' % (NAME, msg))
    elif t == 'warn':
        collectd.warning('%s: %s' % (NAME, msg))
    elif t == 'verb':
        if VERBOSE_LOGGING:
            collectd.info('%s: %s' % (NAME, msg))
    else:
        collectd.notice('%s: %s' % (NAME, msg))


#
# Register our callbacks to collectd
#
collectd.register_config(configure_callback)
collectd.register_read(read_callback)

#
# DEBUG
#
# config_test = collectd.Config('<Module ping_identity> url "https://identity-management.aat.iag-aws.clients.amido.com:9031/pf/heartbeat.ping" type "engine" product "federate"</Module>')
# configure_callback(config_test);
# read_callback();
#
