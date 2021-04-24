<p align="center">
  <a href="https://dev.to/vumdao">
    <img alt="CDK8S Example" src="https://github.com/vumdao/cdk8s-example/blob/master/cover.jpg?raw=true" width="700" />
  </a>
</p>
<h1 align="center">
  <div><b>CDK8S Example</b></div>
</h1>

### **CDK8s is a software development framework for defining Kubernetes applications and reusable abstractions using familiar programming languages and rich object-oriented APIs. CDK8s generates pure Kubernetes YAML - you can use CDK8s to define applications for any Kubernetes cluster running anywhere.**

<h1 align="center">
  <br>
  <img alt="CDK8S Example" src="https://github.com/vumdao/cdk8s-example/blob/master/flow.png?raw=true" width="500" />
</h1>

### **This post provides you some examples of cdk8s python code to create k8s deployments, services, readiness and livness probes, statefulset, persitent volume and cronjob**
<h1 align="center">
  <br>
  <img alt="CDK8S Example" src="https://github.com/vumdao/cdk8s-example/blob/master/logo.png?raw=true" width="200" />
</h1>

---

## What’s In This Document
- [Getting Started With cdk8s](#-Getting-Started-With-cdk8s)
- [Create cluster IP deployment and target port service](#-Create-cluster-IP-deployment-and-target-port-service)
- [Create deployment app with readiness and liveness probes](#-Create-deployment-app-with-readiness-and-liveness-probes)
- [Create statefulset with persisten volume](#-Create-statefulset-with-persisten-volume)
- [Create secret attach to deployment](#-Create-secret-attach-to-deployment)
- [Create cronjob with persistent volume claim](#-Create-cronjob-with-persistent-volume-claim)
- [Conclusion](#-Conclusion)

---

### 🚀 **[Getting Started With cdk8s](#-Getting-Started-With-cdk8s)**
[Getting Started](https://cdk8s.io/docs/v1.0.0-beta.11/getting-started/)
1. Prerequisites

- Python >= 3.7.7
- pipenv version 2018.11.26 or above.

2. New Project

```
$ mkdir hello
$ cd hello
$ cdk8s init python-app
Initializing a project from the python-app template
```

### 🚀 **[Create cluster IP deployment and target port service](#-Create-cluster-IP-deployment-and-target-port-service)**
- https://github.com/vumdao/cdk8s-example/blob/master/clusterip.py

```
from constructs import Construct
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
```

- https://github.com/vumdao/cdk8s-example/blob/master/main.py

```
#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from clusterip import ClusterIp


class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        ClusterIp(self, 'clusterip')


app = App()
MyChart(app, "clusterip")

app.synth()
```

2. Run
```
⚡ $ cdk8s synth
dist/clusterip.k8s.yaml

⚡ $ cat dist/clusterip.k8s.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wappip
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wappip
  template:
    metadata:
      labels:
        app: wappip
      name: wappip
    spec:
      containers:
        - image: katacoda/docker-http-server:latest
          name: wappip
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: wappip
spec:
  ports:
    - name: "80"
      nodePort: 30080
      port: 80
  selector:
    app: wappip
  type: NodePort
---
apiVersion: v1
kind: Service
metadata:
  name: wappip-targetport
spec:
  ports:
    - name: "8080"
      port: 8080
      targetPort: 80
  selector:
    app: wappip
```

### 🚀 **[Create deployment app with readiness and liveness probes](#-Create-deployment-app-with-readiness-and-liveness-probes)**
```
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
```

### 🚀 **[Create statefulset with persisten volume](#-Create-statefulset-with-persisten-volume)**
```
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
```

### 🚀 **[Create secret attach to deployment](#-Create-secret-attach-to-deployment)**
```
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
```

### 🚀 **[Create cronjob with persistent volume claim](#-Create-cronjob-with-persistent-volume-claim)**
```
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
```

### 🚀 **[Conclusion](#-Conclusion)**
cdk8s is just being in beta version, you should consider to use it for production until it reaches a certain level of maturity (probably the first major version)


---

<h3 align="center">
  <a href="https://dev.to/vumdao">:stars: Blog</a>
  <span> · </span>
  <a href="https://github.com/vumdao/cdk8s-example">Github</a>
  <span> · </span>
  <a href="https://stackoverflow.com/users/11430272/vumdao">stackoverflow</a>
  <span> · </span>
  <a href="https://www.linkedin.com/in/vu-dao-9280ab43/">Linkedin</a>
  <span> · </span>
  <a href="https://www.linkedin.com/groups/12488649/">Group</a>
  <span> · </span>
  <a href="https://www.facebook.com/CloudOpz-104917804863956">Page</a>
  <span> · </span>
  <a href="https://twitter.com/VuDao81124667">Twitter :stars:</a>
</h3>

