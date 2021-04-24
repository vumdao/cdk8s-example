from constructs import Construct, Node
from imports import k8s


class DocCronjob(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        app_name = 'doc-clean'
        label = {'app': app_name}
        k8s.KubeCronJobV1Beta1(
            self, "DocCronjob",
            metadata=k8s.ObjectMeta(name=app_name, labels=label),
            spec=k8s.CronJobSpec(
                job_template=k8s.JobTemplateSpec(
                    metadata=k8s.ObjectMeta(name=app_name),
                    spec=k8s.JobSpec(
                        template=k8s.PodTemplateSpec(
                            metadata=k8s.ObjectMeta(name=app_name),
                            spec=k8s.PodSpec(
                                containers=[
                                    k8s.Container(
                                        name=app_name,
                                        image="busybox",
                                        volume_mounts=[k8s.VolumeMount(mount_path='/opt/Documents', name='efs')],
                                        args=['/bin/sh', '-c',
                                              'find /opt/Documents/Viewer/cache -type d -mtime +6 -exec rm -r {} \;; find /opt/Documents/Viewer -type f -mtime +6 -exec rm {} \;'
                                              ]
                                    ),
                                ],
                                restart_policy='OnFailure',
                                volumes=[
                                    k8s.Volume(
                                        name='efs',
                                        persistent_volume_claim=k8s.PersistentVolumeClaimVolumeSource(
                                            claim_name='efs-pvc'
                                        )
                                    )
                                ]
                            )
                        )
                    )
                ),
                schedule='0 1 * * SAT'
            )
        )
