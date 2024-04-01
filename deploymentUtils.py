from kubernetes import client, config
from kubernetes.client.rest import ApiException

'''
This file contains the function for deploying all the k8s cluster components
'''

def create_local_pv(node_name, local_path, pv_name, storage_size):
    # Define the PV
    pv = client.V1PersistentVolume(
        api_version="v1",
        kind="PersistentVolume",
        metadata=client.V1ObjectMeta(name=pv_name),
        spec=client.V1PersistentVolumeSpec(
            capacity={"storage": storage_size},
            volume_mode="Filesystem",
            access_modes=["ReadWriteMany"], # the ResultsHub and a Job should be able to access FS simultaneously
            persistent_volume_reclaim_policy="Retain",
            local=client.V1LocalVolumeSource(path=local_path),
            node_affinity=client.V1VolumeNodeAffinity(
                required=client.V1NodeSelector(
                    node_selector_terms=[
                        client.V1NodeSelectorTerm(
                            match_expressions=[
                                client.V1NodeSelectorRequirement(
                                    key="kubernetes.io/hostname",
                                    operator="In",
                                    values=[node_name]
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )
    # Create the PersistentVolume
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    try:
        api_instance.create_persistent_volume(body=pv)
        print(f"PersistentVolume '{pv_name}' created.")
    except ApiException as e:
        if e.status == 409:
            print(f"PersistentVolume '{pv_name}' already exists.")
        else:
            print(f"Exception when creating PersistentVolume: {e}")
            raise

def create_pvc(pvc_name, storage_size, namespace):
    # Define the PVC
    pvc = client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(name=pvc_name),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            resources=client.V1ResourceRequirements(
                requests={"storage": storage_size}
            )
        )
    )
    # Create the PVC
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    try:
        api_instance.create_namespaced_persistent_volume_claim(namespace=namespace, body=pvc)
        print(f"PersistentVolumeClaim '{pvc_name}' created in namespace '{namespace}'.")
    except ApiException as e:
        if e.status == 409:
            print(f"PersistentVolumeClaim '{pvc_name}' already exists in namespace '{namespace}'.")
        else:
            print(f"Exception when creating PersistentVolumeClaim: {e}")
            raise

def deploy_resultsHub_to_statefulset(pvc_name, namespace):
    config.load_kube_config()  # Load kubeconfig
    api_instance = client.AppsV1Api()

    # Define the StatefulSet
    statefulset = client.V1StatefulSet(
        api_version="apps/v1",
        kind="StatefulSet",
        metadata=client.V1ObjectMeta(
            name="results-hub",
            namespace=namespace
        ),
        spec=client.V1StatefulSetSpec(
            selector=client.V1LabelSelector(
                match_labels={"app": "results-hub"}
            ),
            service_name="results-hub",
            replicas=1,  # Ensure only 1 pod is created
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "results-hub"},
                    # disable AppArmor
                    annotations={
                        "container.apparmor.security.beta.kubernetes.io/results-hub": "unconfined"
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="results-hub",
                        image="yizhuoliang/results-hub:latest",
                        volume_mounts=[client.V1VolumeMount(mount_path="/app/data", name="storage")],
                        ports=[client.V1ContainerPort(container_port=50051)]
                    )],
                    volumes=[
                        client.V1Volume(
                            name="storage",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
                        )
                    ],
                    tolerations=[  # Add this tolerations section
                        client.V1Toleration(
                            key="node-role.kubernetes.io/control-plane",
                            operator="Exists",
                            effect="NoSchedule"
                        )
                    ]
                )
            )
        )
    )
    # Create the StatefulSet
    try:
        api_instance.create_namespaced_stateful_set(namespace=namespace, body=statefulset)
        print(f"StatefulSet 'results-hub' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when creating StatefulSet: {e}")
        raise

    # Define and create a Service to expose the StatefulSet
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name="results-hub-service",
            namespace=namespace
        ),
        spec=client.V1ServiceSpec(
            selector={"app": "results-hub"},
            ports=[client.V1ServicePort(port=30051, target_port=50051, node_port=30051)],
            type="NodePort"
        )
    )

    try:
        api_instance = client.CoreV1Api()
        api_instance.create_namespaced_service(namespace=namespace, body=service)
        print(f"Service 'results-hub-service' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when creating Service: {e}")
        raise

    print("StatefulSet created.")

def deploy_stateless_job(image_name, tag, namespace):
    config.load_kube_config()  # Load kubeconfig
    api_instance = client.BatchV1Api()

    image_name_no_repo = image_name.split('/', 1)[1];
    job_name = f"j2k-job-{image_name_no_repo}-{tag}" # note we remove the repo name here

    # Define the Job
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": job_name}),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="jup2kub-job",
                        image=f"{image_name}:{tag}",
                    )],
                    restart_policy="Never"  # Ensure the container exits after completion
                )
            )
        )
    )

    try:
        api_instance.create_namespaced_job(namespace=namespace, body=job)
        print(f"Job '{job_name}' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when creating Job: {e}")
        raise

def deploy_file_access_job(image_name, tag, namespace, pvc_name):
    config.load_kube_config()  # Load kubeconfig
    api_instance = client.BatchV1Api()

    image_name_no_repo = image_name.split('/', 1)[1]
    job_name = f"j2k-job-{image_name_no_repo}-{tag}"  # note we remove the repo name here

    # Define the job
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": job_name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="jup2kub-job",
                            image=f"{image_name}:{tag}",
                            volume_mounts=[
                                client.V1VolumeMount(
                                    mount_path="/data",  # The path inside the container
                                    name="storage"
                                )
                            ]
                        )
                    ],
                    restart_policy="Never",
                    volumes=[
                        client.V1Volume(
                            name="storage",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name=pvc_name
                            )
                        )
                    ],
                    affinity=client.V1Affinity(
                        node_affinity=client.V1NodeAffinity(
                            required_during_scheduling_ignored_during_execution=client.V1NodeSelector(
                                node_selector_terms=[
                                    client.V1NodeSelectorTerm(
                                        match_expressions=[
                                            client.V1NodeSelectorRequirement(
                                                key="node-role.kubernetes.io/master",
                                                operator="Exists"
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    )
                )
            )
        )
    )

    # Create the job
    try:
        api_instance.create_namespaced_job(namespace=namespace, body=job)
        print(f"Job '{job_name}' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when creating Job: {e}")
        raise