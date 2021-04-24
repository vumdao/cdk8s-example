from constructs import Construct
from imports import k8s
import re


class ReadinessLivenesProbes(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        for _name in ['frontend', 'bad-frontend']:
            if re.search('bad', _name):
                image_tag = 'unhealthy'
                toleration = k8s.Toleration()
                affinity = k8s.Affinity()
            else:
                image_tag = 'health'
                toleration = k8s.Toleration(
                    effect='NoSchedule', key='fe', operator='Equal', value='healthy'
                )
                affinity = k8s.Affinity(
                    node_affinity=k8s.NodeAffinity(
                        required_during_scheduling_ignored_during_execution=k8s.NodeSelector(
                            node_selector_terms=[
                                k8s.NodeSelectorTerm(
                                    match_expressions=[
                                        k8s.NodeSelectorRequirement(
                                            key='kubernetes.io/hostname', operator='In', values=['kube1']
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            label = {'app': _name}
            k8s.KubeDeployment(
                self, f"FrontendHealthy{_name}",
                metadata=k8s.ObjectMeta(labels=label, name=_name),
                spec=k8s.DeploymentSpec(
                    replicas=1,
                    selector=k8s.LabelSelector(match_labels=label),
                    template=k8s.PodTemplateSpec(
                        metadata=k8s.ObjectMeta(labels=label),
                        spec=k8s.PodSpec(
                            containers=[
                                k8s.Container(
                                    name=_name,
                                    image=f"katacoda/docker-http-server:{image_tag}",
                                    ports=[k8s.ContainerPort(container_port=80)],
                                    resources=k8s.ResourceRequirements(
                                        limits={"memory": k8s.Quantity.from_string('3000Mi'),
                                                "cpu": k8s.Quantity.from_string('1000m')},
                                        requests={"memory": k8s.Quantity.from_string('300Mi'),
                                                  "cpu": k8s.Quantity.from_string('200m')}
                                    ),
                                    readiness_probe=k8s.Probe(
                                        http_get=k8s.HttpGetAction(port=k8s.IntOrString.from_number(80), path='/'),
                                        initial_delay_seconds=1, timeout_seconds=1
                                    ),
                                    liveness_probe=k8s.Probe(
                                        http_get=k8s.HttpGetAction(port=k8s.IntOrString.from_number(80), path='/'),
                                        initial_delay_seconds=1, failure_threshold=3, timeout_seconds=1
                                    )
                                )
                            ],
                            tolerations=[toleration],
                            affinity=affinity
                        )
                    )
                )
            )
