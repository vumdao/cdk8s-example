from constructs import Construct, Node
from imports import k8s


class StateFulSet(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        msql_name = 'msql'
        msql_label = {'ss': msql_name}
        k8s.KubeStatefulSet(
            self, "MsqlStatefulSet",
            metadata=k8s.ObjectMeta(name=msql_name),
            spec=k8s.StatefulSetSpec(
                replicas=1,
                selector=k8s.LabelSelector(match_labels=msql_label),
                service_name=msql_name,
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=msql_label, name=msql_name),
                    spec=k8s.PodSpec(
                        containers=[k8s.Container(
                            name=msql_name,
                            image="openshift/mysql-55-centos7",
                            ports=[k8s.ContainerPort(container_port=3306)],
                            env=[
                                k8s.EnvVar(name='MYSQL_ROOT_PASSWORD', value='yourpassword'),
                                k8s.EnvVar(name='MYSQL_USER', value='wp_user'),
                                k8s.EnvVar(name='MYSQL_PASSWORD', value='wp_pass'),
                                k8s.EnvVar(name='MYSQL_DATABASE', value='wp_db'),
                            ],
                            volume_mounts=[k8s.VolumeMount(mount_path='/var/lib/mysql/data',
                                                           name='mysql-persistent-storage')]
                        )]
                    )
                ),
                volume_claim_templates=[
                    k8s.KubePersistentVolumeClaimProps(
                        metadata=k8s.ObjectMeta(name="mysql-persistent-storage"),
                        spec=k8s.PersistentVolumeClaimSpec(
                            access_modes=["ReadWriteOnce"],
                            resources=k8s.ResourceRequirements(requests={"storage": k8s.Quantity.from_string("2Gi")})
                        )
                    )
                ]
            )
        )

        k8s.KubePersistentVolume(
            self, "STSPersistentVolume1",
            metadata=k8s.ObjectMeta(name='nfs-0001'),
            spec=k8s.PersistentVolumeSpec(
                access_modes=['ReadWriteOnce', 'ReadWriteMany'],
                capacity={'storage': k8s.Quantity.from_string('2Gi')},
                nfs=k8s.NfsVolumeSource(path='/exports/data-0001', server='192.168.121.210'),
                persistent_volume_reclaim_policy='Retain'
            )
        )

        k8s.KubePersistentVolume(
            self, "STSPersistentVolume2",
            metadata=k8s.ObjectMeta(name='nfs-0002'),
            spec=k8s.PersistentVolumeSpec(
                access_modes=['ReadWriteOnce', 'ReadWriteMany'],
                capacity={'storage': k8s.Quantity.from_string('5Gi')},
                nfs=k8s.NfsVolumeSource(path='/exports/data-0002', server='192.168.121.210'),
                persistent_volume_reclaim_policy='Retain'
            )
        )
