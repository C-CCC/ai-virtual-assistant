"""
AI Virtual Assistant Infrastructure for DataRobot Codespaces using Pulumi
This provides Infrastructure as Code optimized for DataRobot Codespaces deployment
"""

import pulumi
import pulumi_kubernetes as k8s
import pulumi_random as random
import json
import os
from typing import Optional

# Configuration
config = pulumi.Config()
datarobot_config = config.require_object("datarobot")
codespaces_config = config.require_object("codespaces")
infra_config = config.require_object("infrastructure")

# Environment variables for DataRobot
datarobot_api_token = os.getenv("DATAROBOT_API_TOKEN")
datarobot_endpoint = os.getenv("DATAROBOT_ENDPOINT")
datarobot_project_id = os.getenv("DATAROBOT_PROJECT_ID")

# Validate required environment variables
if not datarobot_api_token:
    raise ValueError("DATAROBOT_API_TOKEN environment variable is required")
if not datarobot_endpoint:
    raise ValueError("DATAROBOT_ENDPOINT environment variable is required")

# Generate random passwords for local services
postgres_password = random.RandomPassword("postgres-password", length=16, special=True)
redis_password = random.RandomPassword("redis-password", length=16, special=True)

# Create namespace for Codespaces
namespace = k8s.core.v1.Namespace("ai-virtual-assistant-codespaces",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ai-virtual-assistant-codespaces",
        labels={
            "app": "ai-virtual-assistant",
            "environment": "codespaces",
            "datarobot-project": datarobot_project_id or "default"
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
        "api-token": datarobot_api_token,
        "endpoint": datarobot_endpoint,
        "llm-deployment-id": os.getenv("DATAROBOT_LLM_DEPLOYMENT_ID", ""),
        "embedding-deployment-id": os.getenv("DATAROBOT_EMBEDDING_DEPLOYMENT_ID", ""),
        "rerank-deployment-id": os.getenv("DATAROBOT_RERANK_DEPLOYMENT_ID", ""),
        "project-id": datarobot_project_id or ""
    }
)

# Local PostgreSQL deployment (if not using managed service)
if not infra_config.get("use_managed_postgres", False):
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
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"memory": "256Mi", "cpu": "100m"},
                            limits={"memory": "512Mi", "cpu": "200m"}
                        )
                    )]
                )
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

# Local Redis deployment (if not using managed service)
if not infra_config.get("use_managed_redis", False):
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
                        command=["redis-server", "--requirepass", redis_password.result],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"memory": "128Mi", "cpu": "50m"},
                            limits={"memory": "256Mi", "cpu": "100m"}
                        )
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

# Local Milvus deployment (always local in Codespaces for development)
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
                    ],
                    resources=k8s.core.v1.ResourceRequirementsArgs(
                        requests={"memory": "512Mi", "cpu": "200m"},
                        limits={"memory": "1Gi", "cpu": "500m"}
                    )
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

# Agent services deployment (optimized for Codespaces)
agent_deployment = k8s.apps.v1.Deployment("agent-services",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="agent-services",
        namespace=namespace.metadata.name,
        labels={"app": "agent-services"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=infra_config.get("agent_replicas", 1),
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
                        k8s.core.v1.EnvVarArgs(name="DATAROBOT_ENDPOINT", value=datarobot_endpoint),
                        k8s.core.v1.EnvVarArgs(name="APP_CACHE_URL", value="redis:6379"),
                        k8s.core.v1.EnvVarArgs(name="APP_DATABASE_URL", value="postgres:5432"),
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=postgres_password.result),
                        k8s.core.v1.EnvVarArgs(name="REDIS_PASSWORD", value=redis_password.result),
                        k8s.core.v1.EnvVarArgs(name="ENVIRONMENT", value="codespaces"),
                        k8s.core.v1.EnvVarArgs(name="DATAROBOT_PROJECT_ID", value=datarobot_project_id or "")
                    ],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                            name=datarobot_secrets.metadata.name
                        )
                    )],
                    resources=k8s.core.v1.ResourceRequirementsArgs(
                        requests={"memory": "256Mi", "cpu": "100m"},
                        limits={"memory": "512Mi", "cpu": "200m"}
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

# Analytics services deployment
analytics_deployment = k8s.apps.v1.Deployment("analytics-services",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="analytics-services",
        namespace=namespace.metadata.name,
        labels={"app": "analytics-services"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=infra_config.get("analytics_replicas", 1),
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "analytics-services"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "analytics-services"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="analytics-services",
                    image="ai-virtual-assistant/analytics:latest",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=8001)],
                    env=[
                        k8s.core.v1.EnvVarArgs(name="APP_LLM_MODELENGINE", value="datarobot"),
                        k8s.core.v1.EnvVarArgs(name="DATAROBOT_ENDPOINT", value=datarobot_endpoint),
                        k8s.core.v1.EnvVarArgs(name="APP_CACHE_URL", value="redis:6379"),
                        k8s.core.v1.EnvVarArgs(name="APP_DATABASE_URL", value="postgres:5432"),
                        k8s.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=postgres_password.result),
                        k8s.core.v1.EnvVarArgs(name="REDIS_PASSWORD", value=redis_password.result),
                        k8s.core.v1.EnvVarArgs(name="ENVIRONMENT", value="codespaces")
                    ],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                            name=datarobot_secrets.metadata.name
                        )
                    )],
                    resources=k8s.core.v1.ResourceRequirementsArgs(
                        requests={"memory": "256Mi", "cpu": "100m"},
                        limits={"memory": "512Mi", "cpu": "200m"}
                    )
                )]
            )
        )
    )
)

# Analytics service
analytics_service = k8s.core.v1.Service("analytics-services",
    metadata=k8s.meta_v1.ObjectMetaArgs(
        name="analytics-services",
        namespace=namespace.metadata.name
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "analytics-services"},
        ports=[k8s.core.v1.ServicePortArgs(port=8001, target_port=8001)],
        type="ClusterIP"
    )
)

# Ingress for Codespaces (using DataRobot's ingress controller)
ingress = k8s.networking.v1.Ingress("ai-virtual-assistant-ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ai-virtual-assistant-ingress",
        namespace=namespace.metadata.name,
        annotations={
            "kubernetes.io/ingress.class": "datarobot-ingress",
            "datarobot.com/project-id": datarobot_project_id or "default",
            "datarobot.com/environment": "codespaces"
        }
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        rules=[k8s.networking.v1.IngressRuleArgs(
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

# Export important values for Codespaces
pulumi.export("namespace", namespace.metadata.name)
pulumi.export("environment", "codespaces")
pulumi.export("datarobot_project_id", datarobot_project_id or "default")
pulumi.export("agent_service_url", f"http://{agent_service.metadata.name}.{namespace.metadata.name}.svc.cluster.local:8000")
pulumi.export("analytics_service_url", f"http://{analytics_service.metadata.name}.{namespace.metadata.name}.svc.cluster.local:8001")
pulumi.export("postgres_password", postgres_password.result)
pulumi.export("redis_password", redis_password.result)
