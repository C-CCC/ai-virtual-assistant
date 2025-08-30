"""
AI Virtual Assistant Infrastructure on DataRobot using Pulumi
This provides Infrastructure as Code for production deployment
"""

import pulumi
import pulumi_kubernetes as k8s
import pulumi_docker as docker
import pulumi_random as random
import json
import os

# Configuration
config = pulumi.Config()
datarobot_config = config.require_object("datarobot")

# Generate random passwords for databases
postgres_password = random.RandomPassword("postgres-password", length=16, special=True)
redis_password = random.RandomPassword("redis-password", length=16, special=True)

# Create namespace
namespace = k8s.core.v1.Namespace("ai-virtual-assistant",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ai-virtual-assistant",
        labels={
            "app": "ai-virtual-assistant",
            "environment": "production"
        }
    )
)

# Create DataRobot secrets
datarobot_secrets = k8s.core.v1.Secret("datarobot-secrets",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="datarobot-secrets",
        namespace=namespace.metadata.name
    ),
    type="Opaque",
    data={
        "api-token": datarobot_config["api_token"],
        "llm-deployment-id": datarobot_config["deployments"]["llm"]["id"],
        "embedding-deployment-id": datarobot_config["deployments"]["embedding"]["id"],
        "rerank-deployment-id": datarobot_config["deployments"]["rerank"]["id"]
    }
)

# PostgreSQL deployment
postgres_deployment = k8s.apps.v1.Deployment("postgres",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="postgres",
        namespace=namespace.metadata.name,
        labels={"app": "postgres"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "postgres"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "postgres"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="postgres",
                    image="postgres:15",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=5432)],
                    env=[
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=postgres_password.result),
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_DB", value="postgres"),
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_USER", value="postgres")
                    ],
                    volume_mounts=[k8s.core.v1.VolumeMountArgs(
                        name="postgres-storage",
                        mount_path="/var/lib/postgresql/data"
                    )]
                )],
                volumes=[k8s.core.v1.VolumeArgs(
                    name="postgres-storage",
                    persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                        claim_name="postgres-pvc"
                    )
                )]
            )
        )
    )
)

# PostgreSQL PVC
postgres_pvc = k8s.core.v1.PersistentVolumeClaim("postgres-pvc",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="postgres-pvc",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        resources=k8s.core.v1.ResourceRequirementsArgs(
            requests={"storage": "10Gi"}
        )
    )
)

# PostgreSQL service
postgres_service = k8s.core.v1.Service("postgres",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="postgres",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "postgres"},
        ports=[k8s.core.v1.ServicePortArgs(port=5432, target_port=5432)],
        type="ClusterIP"
    )
)

# Redis deployment
redis_deployment = k8s.apps.v1.Deployment("redis",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="redis",
        namespace=namespace.metadata.name,
        labels={"app": "redis"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "redis"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "redis"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="redis",
                    image="redis:7-alpine",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=6379)],
                    command=["redis-server", "--requirepass", redis_password.result]
                )]
            )
        )
    )
)

# Redis service
redis_service = k8s.core.v1.Service("redis",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="redis",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "redis"},
        ports=[k8s.core.v1.ServicePortArgs(port=6379, target_port=6379)],
        type="ClusterIP"
    )
)

# Milvus deployment (simplified)
milvus_deployment = k8s.apps.v1.Deployment("milvus",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="milvus",
        namespace=namespace.metadata.name,
        labels={"app": "milvus"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "milvus"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "milvus"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="milvus",
                    image="milvusdb/milvus:v2.3.3",
                    ports=[
                        k8s.core.v1.ContainerPortArgs(container_port=19530),
                        k8s.core.v1.ContainerPortArgs(container_port=9091)
                    ],
                    env=[
                        k8s.core.v1.EnvVarArgs(name="ETCD_ENDPOINTS", value="etcd:2379"),
                        k8s.core.v1.EnvVarArgs(name="MINIO_ADDRESS", value="minio:9010")
                    ]
                )]
            )
        )
    )
)

# Milvus service
milvus_service = k8s.core.v1.Service("milvus",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="milvus",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "milvus"},
        ports=[
            k8s.core.v1.ServicePortArgs(port=19530, target_port=19530),
            k8s.core.v1.ServicePortArgs(port=9091, target_port=9091)
        ],
        type="ClusterIP"
    )
)

# Agent services deployment
agent_deployment = k8s.apps.v1.Deployment("agent-services",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="agent-services",
        namespace=namespace.metadata.name,
        labels={"app": "agent-services"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=2,  # Scaleable
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "agent-services"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "agent-services"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="agent-services",
                    image="ai-virtual-assistant/agent:latest",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=8000)],
                    env=[
                        k8s.core.v1.EnvVarArgs(name="APP_LLM_MODELENGINE", value="datarobot"),
                        k8s.core.v1.EnvVarArgs(name="DATAROBOT_ENDPOINT", value=datarobot_config["endpoint"]),
                        k8s.core.v1.EnvVarArgs(name="APP_CACHE_URL", value="redis:6379"),
                        k8s.core.v1.EnvVarArgs(name="APP_DATABASE_URL", value="postgres:5432"),
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=postgres_password.result),
                        k8s.core.v1.EnvVarArgs(name="REDIS_PASSWORD", value=redis_password.result)
                    ],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                            name=datarobot_secrets.metadata.name
                        )
                    )],
                    resources=k8s.core.v1.ResourceRequirementsArgs(
                        requests={"memory": "512Mi", "cpu": "250m"},
                        limits={"memory": "1Gi", "cpu": "500m"}
                    )
                )]
            )
        )
    )
)

# Agent services service
agent_service = k8s.core.v1.Service("agent-services",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="agent-services",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "agent-services"},
        ports=[k8s.core.v1.ServicePortArgs(port=8000, target_port=8000)],
        type="ClusterIP"
    )
)

# Ingress for external access
ingress = k8s.networking.v1.Ingress("ai-virtual-assistant-ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ai-virtual-assistant-ingress",
        namespace=namespace.metadata.name,
        annotations={
            "kubernetes.io/ingress.class": "nginx",
            "cert-manager.io/cluster-issuer": "letsencrypt-prod"
        }
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        tls=[k8s.networking.v1.IngressTLSArgs(
            hosts=["ai-assistant.yourdomain.com"],
            secret_name="ai-virtual-assistant-tls"
        )],
        rules=[k8s.networking.v1.IngressRuleArgs(
            host="ai-assistant.yourdomain.com",
            http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                paths=[
                    k8s.networking.v1.HTTPIngressPathArgs(
                        path="/",
                        path_type="Prefix",
                        backend=k8s.networking.v1.IngressBackendArgs(
                            service=k8s.networking.v1.IngressServiceBackendArgs(
                                name=agent_service.metadata.name,
                                port=k8s.networking.v1.ServiceBackendPortArgs(number=8000)
                            )
                        )
                    )
                ]
            )
        )]
    )
)

# Horizontal Pod Autoscaler for agent services
agent_hpa = k8s.autoscaling.v2.HorizontalPodAutoscaler("agent-hpa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="agent-hpa",
        namespace=namespace.metadata.name
    ),
    spec=k8s.autoscaling.v2.HorizontalPodAutoscalerSpecArgs(
        scale_target_ref=k8s.autoscaling.v2.CrossVersionObjectReferenceArgs(
            api_version="apps/v1",
            kind="Deployment",
            name=agent_deployment.metadata.name
        ),
        min_replicas=2,
        max_replicas=10,
        metrics=[
            k8s.autoscaling.v2.MetricSpecArgs(
                type="Resource",
                resource=k8s.autoscaling.v2.ResourceMetricSourceArgs(
                    name="cpu",
                    target=k8s.autoscaling.v2.MetricTargetArgs(
                        type="Utilization",
                        average_utilization=70
                    )
                )
            )
        ]
    )
)

# Export important values
pulumi.export("namespace", namespace.metadata.name)
pulumi.export("postgres_password", postgres_password.result)
pulumi.export("redis_password", redis_password.result)
pulumi.export("agent_service_url", f"http://{agent_service.metadata.name}.{namespace.metadata.name}.svc.cluster.local:8000")
pulumi.export("ingress_host", "ai-assistant.yourdomain.com")
