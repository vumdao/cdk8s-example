from constructs import Construct, Node
from imports import k8s


class ClusterIp(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        app_name = 'wappip'
        label = {'app': app_name}
        k8s.KubeDeployment(
            self, "ClusterIpDeployment",
            metadata=k8s.ObjectMeta(name=app_name),
            spec=k8s.DeploymentSpec(
                replicas=2,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label, name=app_name),
                    spec=k8s.PodSpec(
                        containers=[k8s.Container(
                            name=app_name,
                            image="katacoda/docker-http-server:latest",
                            ports=[k8s.ContainerPort(container_port=80)]
                        )]
                    )
                )
            )
        )

        k8s.KubeService(
            self, 'ClusterIpService',
            metadata=k8s.ObjectMeta(name=app_name),
            spec=k8s.ServiceSpec(
                type='NodePort',
                ports=[k8s.ServicePort(port=80, node_port=30080, name="80")],
                selector=label
            )
        )

        k8s.KubeService(
            self, 'ClusterIpTargetPortService',
            metadata=k8s.ObjectMeta(name=f"{app_name}-targetport"),
            spec=k8s.ServiceSpec(
                ports=[k8s.ServicePort(port=8080, target_port=k8s.IntOrString.from_number(80), name="8080")],
                selector=label
            )
        )
