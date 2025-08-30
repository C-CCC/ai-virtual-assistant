# DataRobot Migration Guide

This guide explains how to migrate the NVIDIA AI Virtual Assistant from using NVIDIA NIM microservices to DataRobot endpoints.

## Overview

The migration replaces three NVIDIA NIM services with DataRobot deployments:
- **LLM Inference**: `nemollm-inference` → DataRobot LLM deployment
- **Embeddings**: `nemollm-embedding` → DataRobot embedding deployment  
- **Reranking**: `ranking-ms` → DataRobot rerank deployment

## Prerequisites

1. **DataRobot Account**: Active DataRobot account with API access
2. **DataRobot Deployments**: Three deployments created in DataRobot:
   - LLM deployment for text generation
   - Embedding deployment for vector embeddings
   - Rerank deployment for document reranking
3. **API Token**: DataRobot API token for authentication

## Migration Steps

### 1. Create DataRobot Deployments

#### LLM Deployment
- Create a new deployment in DataRobot for LLM inference
- Use a model suitable for text generation (e.g., GPT, Llama, etc.)
- Note the deployment ID

#### Embedding Deployment
- Create a deployment for generating embeddings
- Use a model that outputs numerical vectors
- Note the deployment ID

#### Rerank Deployment
- Create a deployment for document reranking
- Use a model that can score document relevance
- Note the deployment ID

### 2. Configure Environment Variables

**Action**: Create and edit a `.env` file with your DataRobot configuration

```bash
# Navigate to your project directory
cd /path/to/your/ai-virtual-assistant

# Create the .env file
touch .env
```

**Then edit the `.env` file** with your actual DataRobot values. You can use any text editor:

```bash
# Option 1: Use nano (simple terminal editor)
nano .env

# Option 2: Use vim (advanced terminal editor)
vim .env

# Option 3: Use VS Code (if installed)
code .env

# Option 4: Use your preferred editor
open .env
```

**Content to put in `.env`**:
```bash
# DataRobot Configuration
DATAROBOT_API_TOKEN=your_actual_api_token_here
DATAROBOT_ENDPOINT=https://app.datarobot.com
DATAROBOT_LLM_DEPLOYMENT_ID=your_actual_llm_deployment_id
DATAROBOT_EMBEDDING_DEPLOYMENT_ID=your_actual_embedding_deployment_id
DATAROBOT_RERANK_DEPLOYMENT_ID=your_actual_rerank_deployment_id

# Model Names (should match your DataRobot deployments)
LLM_MODEL_NAME=your_actual_llm_model_name
EMBEDDING_MODEL_NAME=your_actual_embedding_model_name
RERANK_MODEL_NAME=your_actual_rerank_model_name

# Engine Configuration
LLM_MODEL_ENGINE=datarobot
EMBEDDING_MODEL_ENGINE=datarobot
RANKING_MODEL_ENGINE=datarobot
```

**Important**: Replace all the `your_actual_*` values with your real DataRobot credentials and deployment IDs.

### 3. Docker Compose Deployment

**Action**: Run the Docker Compose command to start services

**Prerequisite**: You should have already created your `.env` file in Step 2 above.

```bash
# Start the services with DataRobot configuration
docker compose -f deploy/compose/docker-compose.yaml -f deploy/compose/docker-compose-datarobot.yaml --env-file .env up -d
```

**What this command does**:
- Uses the base `docker-compose.yaml` file
- Overrides with DataRobot-specific settings from `docker-compose-datarobot.yaml`
- Loads your DataRobot credentials from the `.env` file (created in Step 2)
- Starts all services in the background (`-d` flag)
- The NVIDIA NIM services will NOT be started (only DataRobot endpoints used)
```

**What this command does**:
- Uses the base `docker-compose.yaml` file
- Overrides with DataRobot-specific settings from `docker-compose-datarobot.yaml`
- Loads your DataRobot credentials from the `.env` file
- Starts all services in the background (`-d` flag)
- The NVIDIA NIM services will NOT be started (only DataRobot endpoints used)

### 4. Kubernetes/Helm Deployment

Use the DataRobot values override:

```bash
# Install with DataRobot configuration
helm install ai-virtual-assistant ./deploy/helm \
  -f values.yaml \
  -f values-datarobot.yaml \
  --set global.datarobot.enabled=true \
  --set global.datarobot.api_token=your_token \
  --set global.datarobot.deployments.llm.id=your_llm_id \
  --set global.datarobot.deployments.embedding.id=your_embedding_id \
  --set global.datarobot.deployments.rerank.id=your_rerank_id
```

### 5. Verify Configuration

Check that the services are using DataRobot:

```bash
# Check agent services logs
docker logs agent-services

# Look for: "Using DataRobot LLM model ..."
```

## Configuration Files

### Docker Compose
- `docker-compose-datarobot.yaml`: Override file for DataRobot configuration
- Removes NIM service dependencies

### Helm
- `values-datarobot.yaml`: Values override for DataRobot
- `templates/datarobot_secrets.yaml`: Kubernetes secrets template

### Environment Variables
- `datarobot-config.yaml`: Configuration template with examples

## Architecture Changes

### Before (NVIDIA NIMs)
```
Services → nemollm-inference:8000
Services → nemollm-embedding:9080  
Services → ranking-ms:1976
```

### After (DataRobot)
```
Services → DataRobot API → LLM Deployment
Services → DataRobot API → Embedding Deployment
Services → DataRobot API → Rerank Deployment
```

## Troubleshooting

### Common Issues

1. **Missing API Token**
   - Error: "DataRobot configuration requires api_token and deployment_id"
   - Solution: Set `DATAROBOT_API_TOKEN` environment variable

2. **Invalid Deployment ID**
   - Error: "Failed to initialize DataRobot client"
   - Solution: Verify deployment IDs in DataRobot

3. **API Rate Limits**
   - Error: "Too many requests"
   - Solution: Check DataRobot rate limits and adjust accordingly

4. **Model Output Format**
   - Error: "No prediction returned from DataRobot"
   - Solution: Ensure DataRobot deployments return expected output format

### Debug Mode

Enable debug logging:

```bash
export LOGLEVEL=DEBUG
```

### Health Checks

Verify DataRobot connectivity:

```bash
# Test API token
curl -H "Authorization: Token $DATAROBOT_API_TOKEN" \
  "$DATAROBOT_ENDPOINT/api/v2/users/me/"
```

## Performance Considerations

1. **Latency**: DataRobot API calls may have higher latency than local NIMs
2. **Rate Limits**: Be aware of DataRobot API rate limits
3. **Cost**: Monitor DataRobot usage and costs
4. **Caching**: Consider implementing response caching for frequently used queries

## Rollback Plan

To rollback to NVIDIA NIMs:

1. **Docker Compose**:
   ```bash
   docker compose -f deploy/compose/docker-compose.yaml up -d
   ```

2. **Helm**:
   ```bash
   helm upgrade ai-virtual-assistant ./deploy/helm -f values.yaml
   ```

3. **Environment Variables**:
   ```bash
   export APP_LLM_MODELENGINE=nvidia-ai-endpoints
   export APP_EMBEDDINGS_MODELENGINE=nvidia-ai-endpoints
   export APP_RANKING_MODELENGINE=nvidia-ai-endpoints
   ```

## Support

For issues with:
- **DataRobot**: Contact DataRobot support
- **Migration**: Check logs and configuration
- **Application**: Review application-specific error messages

## Next Steps

After successful migration:
1. Monitor performance and costs
2. Optimize DataRobot deployments
3. Consider implementing caching strategies
4. Update monitoring and alerting
