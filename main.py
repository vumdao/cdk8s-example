#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from clusterip import ClusterIp
from statefulset import StateFulSet
from readinesslivenessprobes import ReadinessLivenesProbes
from secret import Secrete
from docClean import DocCronjob


class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        ClusterIp(self, 'clusterip')


class MyStateful(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        StateFulSet(self, 'statefulset')


class MyReadyLiveProbes(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        ReadinessLivenesProbes(self, 'readliveprobes')


class MySecret(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        Secrete(self, 'secret')


class MyCronJob(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        DocCronjob(self, 'secret')


app = App()
MyChart(app, "clusterip")
MyStateful(app, "stateful")
MyReadyLiveProbes(app, 'readliveprobes')
MySecret(app, 'secret')
MyCronJob(app, 'cronjob')

app.synth()
