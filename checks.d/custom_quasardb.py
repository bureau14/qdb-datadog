
from datadog_checks.utils.subprocess_output import get_subprocess_output
from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "3.9.0.rc2"

class QdbCheck(AgentCheck):
    def check(self, instance):
        cluster_uri = instance['cluster_uri']
        public_key = instance['cluster_public_key']
        security_file = instance['user_security_file']
        node_id = instance['node_id']

        if public_key and security_file:
            metrics, err, retcode = get_subprocess_output(["python3",
                                                           "-m", "qdb_datadog",
                                                           "--cluster", cluster_uri,
                                                           "--node-id", node_id,
                                                           "--prefix", "qdb",
                                                           "--cluster-public-key", public_key,
                                                           "--user-security-file", security_file],
                                                          self.log,
                                                          raise_on_empty_output=True)
        else:
            metrics, err, retcode = get_subprocess_output(["python3",
                                                           "-m", "qdb_datadog",
                                                           "--cluster", cluster_uri,
                                                           "--node-id", node_id,
                                                           "--prefix", "qdb"],
                                                          self.log,
                                                          raise_on_empty_output=True)


        for m in metrics.splitlines():
            k,t,v = m.split(',')

            if t == 'GAUGE':
                self.gauge(k, int(v), tags=['node_id:' + node_id])
            elif t == 'COUNTER':
                self.monotonic_count(k, int(v), tags=['node_id:' + node_id])
            else:
                raise RuntimeError("Unrecognized counter type: '" + t + "'")
