from datadog_checks.utils.subprocess_output import get_subprocess_output
from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "3.3.3"

class QdbCheck(AgentCheck):
    def check(self, instance):
        cluster_uri = instance['cluster_uri']
        node_id = instance['node_id']
        metrics, err, retcode = get_subprocess_output(["python",
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
                self.count(k, int(v))
            else:
                raise RuntimeError("Unrecognized counter type: '" + t + "'")
