# 🗄️ Vector Database Module

Docker configuration and setup for Qdrant vector database, the core storage system for semantic search in Brew Master AI.

## 🎯 Purpose

This module provides the vector database infrastructure that:
- Stores semantic embeddings of processed text data
- Enables fast similarity search for RAG queries
- Scales from local development to production deployment
- Maintains data persistence and reliability

## ✨ Features

### 🔍 Vector Search
- **Semantic Similarity**: Find relevant content using vector embeddings
- **Fast Queries**: Optimized for real-time search performance
- **Scalable Storage**: Handle large datasets efficiently
- **Metadata Support**: Store additional information with vectors

### 🐳 Docker Integration
- **Easy Setup**: One-command deployment with Docker Compose
- **Persistent Storage**: Data survives container restarts
- **Portable**: Works on any system with Docker
- **Production Ready**: Configurable for cloud deployment

### 📊 Management
- **Web Interface**: Built-in dashboard for database management
- **API Access**: RESTful API for programmatic access
- **Health Monitoring**: Built-in health checks and status endpoints
- **Backup Support**: Easy data export and import

## 🚀 Quick Start

### Prerequisites
```bash
# Docker and Docker Compose installed
docker --version
docker compose version
```

### Local Development
```bash
# Start Qdrant
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f qdrant
```

### Access Points
- **API**: http://localhost:6333
- **Dashboard**: http://localhost:6333/dashboard
- **Health Check**: http://localhost:6333/health

## 🏗️ Architecture

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
volumes:
  qdrant_data:
```

### Data Persistence
- **Volume**: `qdrant_data` persists data across restarts
- **Storage Path**: `/qdrant/storage` inside container
- **Backup**: Data can be exported/imported via API

## 📡 API Usage

### Python Client
```python
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="brew_master_ai",
    vectors_config={"size": 384, "distance": "Cosine"}
)

# Search vectors
results = client.search(
    collection_name="brew_master_ai",
    query_vector=[0.1, 0.2, ...],
    limit=10
)
```

### REST API
```bash
# Health check
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Search vectors
curl -X POST "http://localhost:6333/collections/brew_master_ai/points/search" \
  -H "Content-Type: application/json" \
  -d '{"vector": [0.1, 0.2, ...], "limit": 10}'
```

## ⚙️ Configuration

### Environment Variables
```bash
# Qdrant configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your-api-key  # Optional for local dev
```

### Collection Configuration
```python
# Default collection settings
collection_config = {
    "name": "brew_master_ai",
    "vectors": {
        "size": 384,  # Sentence transformer embedding size
        "distance": "Cosine"  # Similarity metric
    },
    "optimizers_config": {
        "default_segment_number": 2
    }
}
```

## 🔧 Management

### Starting/Stopping
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View status
docker compose ps
```

### Data Management
```bash
# Backup data
docker compose exec qdrant qdrant snapshot create

# Restore data
docker compose exec qdrant qdrant snapshot restore

# View storage usage
docker compose exec qdrant df -h /qdrant/storage
```

### Logs and Monitoring
```bash
# View logs
docker compose logs qdrant

# Follow logs
docker compose logs -f qdrant

# Check resource usage
docker stats qdrant
```

## 🧪 Testing

### Health Check
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Expected response
{
  "title": "qdrant",
  "version": "1.7.0",
  "status": "ok"
}
```

### Collection Operations
```python
# Test collection creation
client.create_collection("test_collection", vectors_config={"size": 384, "distance": "Cosine"})

# Test vector insertion
client.upsert("test_collection", points=[{"id": 1, "vector": [0.1]*384, "payload": {"text": "test"}}])

# Test search
results = client.search("test_collection", query_vector=[0.1]*384, limit=1)
```

## 🚀 Production Deployment

### AWS ECS
```yaml
# task-definition.json
{
  "family": "qdrant",
  "containerDefinitions": [
    {
      "name": "qdrant",
      "image": "qdrant/qdrant:latest",
      "portMappings": [{"containerPort": 6333, "hostPort": 6333}],
      "mountPoints": [{"sourceVolume": "qdrant-data", "containerPath": "/qdrant/storage"}]
    }
  ],
  "volumes": [{"name": "qdrant-data", "efsVolumeConfiguration": {...}}]
}
```

### Kubernetes
```yaml
# qdrant-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
```

### Cloud Managed Services
- **Qdrant Cloud**: Managed Qdrant service
- **AWS OpenSearch**: Vector search capabilities
- **Pinecone**: Specialized vector database
- **Weaviate Cloud**: Vector database as a service

## 🔒 Security

### API Key Authentication
```python
# Connect with API key
client = QdrantClient(
    host="your-qdrant-host",
    port=6333,
    api_key="your-api-key"
)
```

### Network Security
```bash
# Restrict access to localhost only
docker compose up -d --scale qdrant=1

# Use reverse proxy for external access
# Configure firewall rules
# Enable SSL/TLS encryption
```

## 📊 Performance

### Optimization Tips
1. **Index Configuration**: Optimize segment numbers for your data size
2. **Memory Usage**: Monitor RAM usage for large collections
3. **Storage**: Use SSD storage for better I/O performance
4. **Network**: Minimize latency between application and database

### Monitoring
```bash
# Check resource usage
docker stats qdrant

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:6333/collections"

# View collection statistics
curl http://localhost:6333/collections/brew_master_ai
```

## 🔍 Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check port availability
lsof -i :6333

# Check Docker logs
docker compose logs qdrant

# Restart Docker service
sudo systemctl restart docker
```

**Connection Refused:**
```bash
# Check if Qdrant is running
docker compose ps

# Check container health
docker compose exec qdrant qdrant health

# Restart container
docker compose restart qdrant
```

**Storage Issues:**
```bash
# Check disk space
df -h

# Check volume permissions
docker compose exec qdrant ls -la /qdrant/storage

# Recreate volume if needed
docker compose down -v
docker compose up -d
```

### Performance Issues
```bash
# Check memory usage
docker stats qdrant

# Monitor CPU usage
top -p $(docker inspect --format='{{.State.Pid}}' qdrant)

# Check network connectivity
docker compose exec qdrant ping google.com
```

## 🔄 Integration

### With Data Extraction Module
The vector database receives embeddings from the data extraction pipeline:
- Text chunks are embedded using sentence-transformers
- Embeddings are uploaded to Qdrant collection
- Metadata includes source file and chunk information

### With Backend Module
The FastAPI backend queries the vector database:
- User queries are embedded using the same model
- Similar vectors are retrieved from Qdrant
- Retrieved chunks are used for RAG responses

## 📚 Resources

### Documentation
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Docker Documentation](https://docs.docker.com/)

### Community
- [Qdrant GitHub](https://github.com/qdrant/qdrant)
- [Qdrant Discord](https://discord.gg/tdtYvXjC4h)
- [Qdrant Blog](https://qdrant.tech/articles/)

## 🎯 Future Enhancements

- [ ] Multi-node clustering for high availability
- [ ] Advanced indexing strategies
- [ ] Real-time replication
- [ ] Advanced filtering and faceted search
- [ ] Integration with monitoring tools
- [ ] Automated backup and recovery
- [ ] Performance benchmarking tools
