from constructs import Construct, Node
from imports import k8s


class Secrete(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        app_name = 'myscecret'
        label = {'app': app_name}
        k8s.KubeDeployment(
            self, "SecreteDeployment",
            metadata=k8s.ObjectMeta(name=app_name),
            spec=k8s.DeploymentSpec(
                replicas=1,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label, name=app_name),
                    spec=k8s.PodSpec(
                        containers=[
                            k8s.Container(
                                name=app_name,
                                image="alpine:latest",
                                ports=[k8s.ContainerPort(container_port=80)],
                                command=['sleep', '9999'],
                                env=[
                                    k8s.EnvVar(
                                        name='SECRET_USERNAME',
                                        value_from=k8s.EnvVarSource(
                                            secret_key_ref=k8s.SecretKeySelector(key='username', name='test-secret')
                                        )
                                    ),
                                    k8s.EnvVar(
                                        name='SECRET_PASSWORD',
                                        value_from=k8s.EnvVarSource(
                                            secret_key_ref=k8s.SecretKeySelector(key='password', name='test-secret')
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        )

        k8s.KubeSecret(
            self, 'Secrete',
            metadata=k8s.ObjectMeta(name='test-secret'),
            type='Opaque',
            data={"username": "YWRtaW4=", "password": "YTYyZmpiZDM3OTQyZGNz"}
        )
