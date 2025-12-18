# SECURAA MongoDB Sharding Scalable Architecture

## Document Version: 1.0
## Last Updated: December 2024

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Current Architecture Overview](#2-current-architecture-overview)
3. [Sharding Architecture Design](#3-sharding-architecture-design)
4. [Component Details](#4-component-details)
5. [Collection Sharding Strategy](#5-collection-sharding-strategy)
6. [High Availability Configuration](#6-high-availability-configuration)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Data Flow Architecture](#8-data-flow-architecture)
9. [Scaling Strategies](#9-scaling-strategies)
10. [Operational Procedures](#10-operational-procedures)
11. [Monitoring and Alerting](#11-monitoring-and-alerting)
12. [Disaster Recovery](#12-disaster-recovery)

---

## 1. Executive Summary

### 1.1 Purpose
This document provides a comprehensive MongoDB sharding architecture for the SECURAA platform - a Security Orchestration, Automation and Response (SOAR) system. The architecture is designed to handle:
- Multi-tenant (MSSP) deployments
- High-volume security incident data
- Real-time case processing
- Scalable integration management
- Enterprise-grade reliability

### 1.2 Key Architecture Decisions
- **Sharding Type**: Range-based and Hashed sharding based on collection access patterns
- **Replica Set Configuration**: 3-node replica sets for all shards
- **Config Servers**: Dedicated 3-node replica set (cfgrs)
- **Query Routers**: Multiple mongos instances behind load balancer
- **Shard Key Strategy**: Tenant-based compound keys for MSSP deployments

### 1.3 Technology Stack
| Component | Version | Purpose |
|-----------|---------|---------|
| MongoDB | 7.0 | Primary Database |
| Go | 1.20+ | Backend Services |
| Docker Swarm | Latest | Container Orchestration |
| Redis | Latest | Caching Layer |
| Kafka | Latest | Message Queue |

---

## 2. Current Architecture Overview

### 2.1 Project Structure
```
SECURAA Platform
├── build_securaa/           # Core build and configuration
│   ├── securaa/common/      # Shared utilities and MongoDB controller
│   ├── pkg/db/              # Database scripts and migrations
│   └── deployment_scripts/  # Docker deployment scripts
├── securaa/                 # Main SOAR service (SIEM integrations)
├── securaa_lib/             # Shared Go library
│   ├── mongoclient/         # MongoDB client wrapper with sharding support
│   ├── config/              # Configuration management
│   ├── common/              # Common utilities
│   └── models/              # Data models
├── zona_services/           # Backend microservices
│   ├── zona_siem/           # SIEM integration service
│   ├── zona_user/           # User management
│   ├── zona_playbook/       # Playbook engine
│   ├── zona_integrations/   # Integration manager
│   ├── zona_shard_handler/  # Shard management service
│   ├── custom_mongodb_shard/# MongoDB shard Docker image
│   └── custom_mongos/       # Mongos Docker image
├── zona_batch/              # Batch processing services
│   ├── zona_case_consumer/  # Case ingestion from SIEMs
│   ├── csam_connector/      # CSAM integration
│   └── sla_breach_monitor/  # SLA monitoring
├── integrations/            # 180+ security integrations
└── sia_service/             # AI/ML service for security insights
```

### 2.2 Current Database Design
```
Databases:
├── fkart_incidents (Core DB)     # Main SOAR database
├── meta_db                        # Sharding metadata
├── admin                          # Authentication
└── tenant_<code>_db              # Per-tenant databases (MSSP)
```

### 2.3 Existing MongoDB Configuration
```yaml
# Current mongod.conf
storage:
  dbPath: /data/db
net:
  bindIpAll: true
  port: 27017
security:
  authorization: enabled
  keyFile: /etc/testkey
```

---

## 3. Sharding Architecture Design

### 3.1 High-Level Architecture Diagram
```mermaid
graph TB
    LB[Load Balancer<br/>HAProxy / AWS ALB / Nginx]
    
    subgraph QueryRouters["Query Router Layer"]
        M1[Mongos #1<br/>Port: 27017]
        M2[Mongos #2<br/>Port: 27017]
        M3[Mongos #3<br/>Port: 27017]
    end
    
    subgraph ConfigLayer["Config Server Replica Set - cfgrs - Port: 28017"]
        CS1[Config Server 1<br/>Primary]
        CS2[Config Server 2<br/>Secondary]
        CS3[Config Server 3<br/>Secondary]
    end
    
    subgraph ShardLayer["Shard Layer"]
        subgraph Shard1["Shard 1 Replica Set - shard1rs - Port: 29017"]
            S1P[Primary<br/>Primary Host]
            S1S[Secondary<br/>Secondary Host]
            S1A[Arbiter<br/>Arbiter Host]
        end
        
        subgraph Shard2["Shard 2 Replica Set - shard2rs - Port: 29018"]
            S2P[Primary<br/>Primary Host]
            S2S[Secondary<br/>Secondary Host]
            S2A[Arbiter<br/>Arbiter Host]
        end
        
        subgraph ShardN["Shard N Replica Set - shardNrs - Port: 29066<br/>Up to 50 shards"]
            SNP[Primary<br/>Primary Host]
            SNS[Secondary<br/>Secondary Host]
            SNA[Arbiter<br/>Arbiter Host]
        end
    end
    
    subgraph MetaLayer["Meta Database Replica Set - metars - Port: 27018"]
        MP[Meta Primary<br/>Primary Host]
        MS[Meta Secondary<br/>Secondary Host]
        MA[Meta Arbiter<br/>Arbiter Host]
    end
    
    LB --> M1
    LB --> M2
    LB --> M3
    
    M1 --> ConfigLayer
    M2 --> ConfigLayer
    M3 --> ConfigLayer
    
    M1 --> ShardLayer
    M2 --> ShardLayer
    M3 --> ShardLayer
    
    ConfigLayer --> MetaLayer
```

### 3.2 Port Allocation Strategy
| Component | Port Range | Purpose |
|-----------|------------|---------|
| Mongos | 27017 | Query Router (Application Connection) |
| Meta DB | 27018 | Sharding Metadata Storage |
| Config Server | 28017 | Sharding Config Replica Set |
| Shard 1 | 29017 | First Data Shard |
| Shard 2 | 29018 | Second Data Shard |
| Shard N | 29017 + (N-1) | Additional Shards (up to 29066) |

### 3.3 Connection String Formats
```go
// Mongos Connection (Recommended for Applications)
mongodb://root:S3cur@A_b3st@mongos1:27017,mongos2:27017,mongos3:27017/?authSource=admin

// Direct Shard Connection (Administrative)
mongodb://root:S3cur@A_b3st@shard1-primary:29017,shard1-secondary:29017/?replicaSet=shard1rs

// Meta DB Connection
mongodb://root:S3cur@A_b3st@meta-primary:27018,meta-secondary:27018/?replicaSet=metars
```

---

## 4. Component Details

### 4.1 Mongos (Query Router)
**Purpose**: Routes queries to appropriate shards based on shard key

**Configuration** (`/etc/mongos.conf`):
```yaml
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongos.log
  logRotate: reopen

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

net:
  bindIpAll: true
  port: 27017

security:
  keyFile: /etc/testkey

sharding:
  configDB: cfgrs/config1:28017,config2:28017,config3:28017
```

**Docker Service** (`zona_services/custom_mongos/Dockerfile`):
```dockerfile
FROM mongo:7.0
COPY config/limits.conf /etc/security/limits.conf
COPY config/mongos.conf /etc/mongos.conf
COPY config/testkey /etc/testkey
RUN chmod 600 /etc/testkey
ENTRYPOINT ["mongos", "-f", "/etc/mongos.conf"]
```

### 4.2 Config Server Replica Set
**Purpose**: Stores cluster metadata, chunk distribution, and shard configuration

**Configuration**:
```yaml
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

storage:
  dbPath: /data/configdb

net:
  bindIpAll: true
  port: 28017

security:
  authorization: enabled
  keyFile: /etc/testkey

replication:
  replSetName: cfgrs

sharding:
  clusterRole: configsvr
```

### 4.3 Shard Servers
**Purpose**: Store distributed data chunks

**Configuration** (`zona_services/custom_mongodb_shard/config/mongod.conf`):
```yaml
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

storage:
  dbPath: /data/db

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

net:
  bindIpAll: true
  port: 27017

security:
  authorization: enabled
  keyFile: /etc/testkey

replication:
  replSetName: shardXrs

sharding:
  clusterRole: shardsvr
```

### 4.4 Meta Database
**Purpose**: Stores sharding configuration, HA status, and cluster membership

**Collections**:
```javascript
// meta_db database
db.createCollection("metadb_members")    // Meta replica set members
db.createCollection("config_servers")    // Config server members
db.createCollection("shards")            // Shard replica set info
db.createCollection("ha_config")         // High availability configuration
```

### 4.5 Shard Handler Service
**Location**: `zona_services/zona_shard_handler/`

**Purpose**: Manages shard lifecycle operations

**Endpoints**:
```go
// Main endpoint for shard management
POST /manageShardService/
```

**Key Functions** (from `securaa_lib/mongoclient/mongoclient.go`):
```go
// Add new shard
func AddNewShardService(mongoDbHost, replicaSetName string, configObject config.ConfigStruct, conf config.Config)

// Remove shard
func RemoveShardService(mongoDbHost, replicaSetName string, configObject config.ConfigStruct, conf config.Config)

// Initialize replica set members
func InitializeMembersInReplicaSet(mongoDbHost, replicaSetName string, replicaSetPort int, members []MemberConfig, configObject config.ConfigStruct)

// Handle removing shards in progress
func HandleRemovingShards(configObject config.ConfigStruct) error
```

---

## 5. Collection Sharding Strategy

### 5.1 Core Collections Analysis

Based on codebase analysis, the following collections require sharding:

#### 5.1.1 High-Volume Collections (Priority: Critical)
| Collection | Shard Key | Strategy | Justification |
|------------|-----------|----------|---------------|
| `zona_incidents` | `{tenantcode: 1, zona_z_incident_id: 1}` | Range | Primary case data, queried by tenant |
| `task_execution` | `{tenantcode: 1, taskid: 1}` | Hashed | High write volume, distributed |
| `playbooks_executions` | `{tenantcode: 1, playbook_id: 1}` | Range | Execution history |
| `auditCollection` | `{tenantcode: 1, date: 1}` | Range | Time-series audit logs |
| `zona_loginfo` | `{tenantcode: 1, _id: 1}` | Hashed | Log aggregation |

#### 5.1.2 Medium-Volume Collections (Priority: High)
| Collection | Shard Key | Strategy | Justification |
|------------|-----------|----------|---------------|
| `active_instance` | `{tenantcode: 1, integration_id: 1}` | Range | Integration instances |
| `playbooks` | `{tenantcode: 1, id: 1}` | Range | Playbook definitions |
| `tasks` | `{tenantcode: 1, id: 1}` | Range | Task definitions |
| `users` | `{tenantcode: 1, id: 1}` | Range | User management |
| `investigation` | `{tenantcode: 1, id: 1}` | Range | Investigation data |

#### 5.1.3 Low-Volume Collections (Unsharded)
| Collection | Justification |
|------------|---------------|
| `integration` | Reference data, ~200 records |
| `tenants` | Master tenant list, low volume |
| `roles` | Permission definitions, static |
| `incident_status` | Enumeration data |
| `incident_severities` | Enumeration data |
| `system` | System configuration |
| `current_release` | Version info |

### 5.2 Sharding Commands

```javascript
// Connect to mongos
mongosh mongodb://root:password@mongos:27017/admin

// Enable sharding on database
sh.enableSharding("fkart_incidents")

// Shard high-volume collections
// Incidents - Range sharding for tenant isolation
sh.shardCollection("fkart_incidents.zona_incidents",
    { "tenantcode": 1, "zona_z_incident_id": 1 })

// Task executions - Hashed for write distribution
sh.shardCollection("fkart_incidents.task_execution",
    { "tenantcode": "hashed" })

// Playbook executions
sh.shardCollection("fkart_incidents.playbooks_executions",
    { "tenantcode": 1, "playbook_id": 1 })

// Audit logs - Range for time-based queries
sh.shardCollection("fkart_incidents.auditCollection",
    { "tenantcode": 1, "date": 1 })

// Active instances
sh.shardCollection("fkart_incidents.active_instance",
    { "tenantcode": 1, "integration_id": 1 })
```

### 5.3 Index Strategy

```javascript
// zona_incidents - Critical indexes
db.zona_incidents.createIndex({ "zona_z_incident_id": 1 }, { name: "incident_id_idx" })
db.zona_incidents.createIndex({ "tenantcode": 1, "status": 1 }, { name: "tenant_status_idx" })
db.zona_incidents.createIndex({ "tenantcode": 1, "createddate": -1 }, { name: "tenant_date_idx" })
db.zona_incidents.createIndex({ "zona_z_instance_id": 1 }, { name: "get_instance_id" })
db.zona_incidents.createIndex({ "tenantcode": 1, "zona_z_severity": 1, "createddate": -1 },
    { name: "tenant_severity_date_idx" })

// task_execution - Performance indexes
db.task_execution.createIndex({ "name": 1, "taskid": 1 }, { name: "utils_task_index" })
db.task_execution.createIndex({ "tenantcode": 1, "status": 1 }, { name: "tenant_status_idx" })

// playbooks_executions
db.playbooks_executions.createIndex({ "tenantcode": 1, "caseid": 1 }, { name: "tenant_case_idx" })
db.playbooks_executions.createIndex({ "tenantcode": 1, "status": 1, "createddate": -1 },
    { name: "tenant_status_date_idx" })

// auditCollection
db.auditCollection.createIndex({ "tenantcode": 1, "date": -1 }, { name: "tenant_date_idx" })
db.auditCollection.createIndex({ "tenantcode": 1, "object": 1, "action": 1 },
    { name: "tenant_object_action_idx" })
```

### 5.4 Chunk Management

```javascript
// Pre-split chunks for known tenants
sh.splitAt("fkart_incidents.zona_incidents", { "tenantcode": "tenant_a", "zona_z_incident_id": MinKey })
sh.splitAt("fkart_incidents.zona_incidents", { "tenantcode": "tenant_b", "zona_z_incident_id": MinKey })
sh.splitAt("fkart_incidents.zona_incidents", { "tenantcode": "tenant_c", "zona_z_incident_id": MinKey })

// Move chunks for tenant isolation (optional)
sh.moveChunk("fkart_incidents.zona_incidents",
    { "tenantcode": "tenant_a", "zona_z_incident_id": MinKey }, "shard1rs")

// Set chunk size (default: 128MB, adjust based on workload)
use config
db.settings.updateOne(
   { _id: "chunksize" },
   { $set: { value: 64 } },  // 64MB for faster balancing
   { upsert: true }
)
```

---

## 6. High Availability Configuration

### 6.1 Replica Set Configuration

**Primary Server Priority Configuration**:
```go
// From securaa_lib/mongoclient/mongoclient.go
func ChangingPriorityOfPrimary(replicaSetConfig bson.M, mongoDbHost string, replicaSetPort int, priority int)
```

**Member Configuration Structure**:
```go
type MemberConfig struct {
    Name       string `json:"name" bson:"name"`
    ServerIP   string `json:"server_ip" bson:"server_ip"`
    Port       int    `json:"port" bson:"port"`
    MemberID   int    `json:"member_id" bson:"member_id"`
    MemberType string `json:"member_type" bson:"member_type"` // "replica" or "arbiter"
    ServerType string `json:"server_type" bson:"server_type"` // "primary", "secondary", "arbiter"
    Status     string `json:"status" bson:"status"`
}
```

### 6.2 Failover Configuration

```javascript
// Replica set configuration with failover settings
rs.reconfig({
    _id: "shard1rs",
    members: [
        { _id: 0, host: "primary:29017", priority: 2 },
        { _id: 1, host: "secondary:29017", priority: 1 },
        { _id: 2, host: "arbiter:29017", arbiterOnly: true }
    ],
    settings: {
        heartbeatTimeoutSecs: 10,
        electionTimeoutMillis: 10000,
        catchUpTimeoutMillis: 60000
    }
})
```

### 6.3 Connection Pool Settings

From `securaa_lib/mongoclient/mongoclient.go`:
```go
func GetMongosClient(conf config.Config) (*mongo.Client, *options.ClientOptions, error) {
    clientOptions := options.Client().
        ApplyURI(uri).
        SetRetryWrites(true).
        SetMaxPoolSize(50).                          // Maximum connections
        SetMinPoolSize(5).                           // Minimum connections
        SetServerSelectionTimeout(30 * time.Second). // Time to find mongos
        SetConnectTimeout(30 * time.Second).         // TCP connection timeout
        SetSocketTimeout(2 * time.Minute).           // Long-running ops timeout
        SetHeartbeatInterval(5 * time.Second)        // Node liveness checks
    // ...
}

func GetMongoClientV2(configStruct config.ConfigStruct, replicaSetName, mongoHost string, mongodbPort int) {
    clientOptions.SetMaxPoolSize(200)
    clientOptions.SetMaxConnIdleTime(30 * time.Second)
    // ...
}
```

### 6.4 Read/Write Concerns

```go
// Recommended settings for SECURAA
// Write Concern: majority for critical operations
writeConcern := writeconcern.Majority()
writeConcern.WTimeout = 5 * time.Second

// Read Concern: majority for consistency
readConcern := readconcern.Majority()

// Read Preference: primaryPreferred for read-heavy ops
readPref := readpref.PrimaryPreferred()
```

---

## 7. Deployment Architecture

### 7.1 Docker Swarm Deployment

**Service Stack Definition**:
```yaml
version: '3.8'

services:
  # Mongos Query Routers
  mongos:
    image: 665853670667.dkr.ecr.us-east-2.amazonaws.com/custom_mongos:mongo_7.0
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == manager
    ports:
      - "27017:27017"
    networks:
      - securaa-swarm
    secrets:
      - mongodb_keyfile

  # Config Server Replica Set
  config_server:
    image: 665853670667.dkr.ecr.us-east-2.amazonaws.com/custom_mongodb_shard:mongo_7.0
    deploy:
      replicas: 3
      placement:
        max_replicas_per_node: 1
    ports:
      - "28017:27017"
    volumes:
      - config_data:/data/configdb
    command: ["mongod", "--configsvr", "--replSet", "cfgrs", "--port", "27017", "--keyFile", "/etc/testkey"]
    networks:
      - securaa-swarm

  # Meta Database Replica Set
  meta_db:
    image: 665853670667.dkr.ecr.us-east-2.amazonaws.com/custom_mongodb_replica:mongoreplic_7.0
    deploy:
      replicas: 3
      placement:
        max_replicas_per_node: 1
    ports:
      - "27018:27017"
    volumes:
      - meta_data:/data/db
    networks:
      - securaa-swarm

  # Shard Handler Service
  zona_shard_handler:
    image: 665853670667.dkr.ecr.us-east-2.amazonaws.com/zona_shard_handler:dev_6.0
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    ports:
      - "8253:8253"
    networks:
      - securaa-swarm

volumes:
  config_data:
  meta_data:
  shard1_data:
  shard2_data:

networks:
  securaa-swarm:
    external: true

secrets:
  mongodb_keyfile:
    external: true
```

### 7.2 Shard Provisioning Process

**Add New Shard** (from `securaa_lib/mongoclient/mongoclient.go`):
```go
func setupNewShard(cli *client.Client, mongoDbHost string, replicaSet ReplicaSet,
    configObject config.ConfigStruct, conf config.Config) string {

    // 1. Create shard service with no auth (initial setup)
    serviceCtx := docker.MongoShardServiceContext(serviceName,
        common.MONGO_SHARDING_NOAUTH_DOCKER_TAG, shardPort, 1,
        replicaSetName, common.CLUSTERROLE_SHARD_SERVER)

    // 2. Initialize as replica set
    err = InitializeReplicaSet(mongoShardDbClient, mongoDbHost,
        strconv.Itoa(shardPort), replicaSetName)

    // 3. Create MongoDB user
    err = CreateMongoUser(mongoShardDbClient, conf)

    // 4. Recreate with auth enabled
    serviceCtx = docker.MongoShardServiceContext(serviceName,
        common.MONGODB_DOCKER_TAG, shardPort, 1,
        replicaSetName, common.CLUSTERROLE_SHARD_SERVER)

    // 5. Add shard to cluster via mongos
    result, err := AddNewShard(mongosClient, mongoDbHost,
        strconv.Itoa(shardPort), replicaSetName)

    return ""
}
```

### 7.3 Environment Configuration

**Required Environment Variables**:
```bash
# MongoDB Connection
MONGO_DB_HOST=primary-host-ip
MONGO_PORT=27017
MONGO_USERNAME=root
MONGO_PASSWORD=S3cur@A_b3st
MONGO_AUTH_DB=admin
MONGO_DATABASE=fkart_incidents

# Sharding Configuration
CONFIG_SERVER_RS=cfgrs
CONFIG_SERVER_HOSTS=config1:28017,config2:28017,config3:28017
META_DB_RS=metars
META_DB_PORT=27018

# Docker Registry
DOCKER_REGISTRY=665853670667.dkr.ecr.us-east-2.amazonaws.com
MONGODB_DOCKER_TAG=mongo_7.0
MONGODB_REPLICA_TAG=mongoreplic_7.0
```

---

## 8. Data Flow Architecture

### 8.1 Write Path
```mermaid
graph LR
    SIEM[SIEM/<br/>Integration]
    ZS[zona_siem<br/>Go Service]
    M[Mongos<br/>Query Router]
    SP[Shard<br/>Primary]
    SS[Shard<br/>Secondary]
    
    SIEM --> ZS
    ZS --> M
    M --> SP
    SP --> SS
```

### 8.2 Read Path
```mermaid
graph TB
    UI[UI/API<br/>Request]
    M[Mongos<br/>Query Router]
    SG{If scatter-<br/>gather query}
    SD[Shard<br/>based on<br/>shard key]
    S1[Shard 1]
    S2[Shard 2]
    SN[Shard N]
    
    UI --> M
    M --> SG
    SG -->|Single Shard| SD
    SG -->|Multiple Shards| S1
    SG -->|Multiple Shards| S2
    SG -->|Multiple Shards| SN
```

### 8.3 Case Ingestion Flow
```mermaid
graph LR
    subgraph CaseIngestion["Case Ingestion Pipeline"]
        SIEM[SIEM<br/>QRadar<br/>Splunk<br/>Sentinel]
        KAFKA[Kafka<br/>Topic: case_queue]
        CONSUMER[zona_case_consumer<br/>Batch]
        INCIDENTS[zona_incidents<br/>Collection<br/>Sharded]
        
        SIEM --> KAFKA
        KAFKA --> CONSUMER
        CONSUMER --> INCIDENTS
    end
    
    CONTROLLERS[Controllers zona_batch/zona_case_consumer/controllers/:<br/>• qradarController.go<br/>• splunkController.go<br/>• azuresentinelController.go<br/>• wazuhController.go<br/>• crowdstrikeController.go<br/>• elasticController.go<br/>• sentinelOneController.go<br/>• securonixController.go]
    
    CONSUMER -.-> CONTROLLERS
```

---

## 9. Scaling Strategies

### 9.1 Horizontal Scaling

**Add Shard via API**:
```bash
# Using zona_shard_handler service
curl -X POST http://zona_shard_handler:8253/manageShardService/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "replicaSet": "shard3rs",
    "memberConfig": {
      "name": "mongo_shard3_repl",
      "port": 29019,
      "memberType": "replica"
    }
  }'
```

**Scaling Triggers**:
| Metric | Threshold | Action |
|--------|-----------|--------|
| Chunk Count per Shard | > 1000 | Add new shard |
| Storage Utilization | > 70% | Add new shard |
| Query Latency P95 | > 500ms | Scale mongos, add indexes |
| Connection Count | > 80% pool | Increase pool size |

### 9.2 Vertical Scaling

**Resource Recommendations**:
| Component | CPU | RAM | Storage | IOPS |
|-----------|-----|-----|---------|------|
| Mongos | 4 cores | 8GB | 50GB SSD | 1000 |
| Config Server | 2 cores | 4GB | 100GB SSD | 500 |
| Shard Primary | 8 cores | 32GB | 500GB SSD | 3000 |
| Shard Secondary | 8 cores | 32GB | 500GB SSD | 2000 |
| Arbiter | 1 core | 1GB | 10GB | 100 |

### 9.3 Auto-Scaling Configuration

```yaml
# Docker Swarm auto-scaling (via external orchestrator)
scaling:
  mongos:
    min_replicas: 2
    max_replicas: 10
    target_cpu_utilization: 70%

  zona_siem:
    min_replicas: 2
    max_replicas: 20
    target_cpu_utilization: 60%

  zona_playbook:
    min_replicas: 2
    max_replicas: 15
    target_cpu_utilization: 65%
```

---

## 10. Operational Procedures

### 10.1 Adding a New Shard

```bash
# Step 1: Deploy shard replica set containers
docker service create \
  --name mongo_shard3_repl \
  --replicas 1 \
  --network securaa-swarm \
  --publish 29019:27017 \
  --mount type=volume,source=shard3_data,target=/data/db \
  665853670667.dkr.ecr.us-east-2.amazonaws.com/custom_mongodb_shard:mongo_7.0

# Step 2: Initialize replica set
mongosh mongodb://shard3-host:29019 --eval '
rs.initiate({
  _id: "shard3rs",
  members: [
    { _id: 0, host: "shard3-primary:29019", priority: 2 },
    { _id: 1, host: "shard3-secondary:29019", priority: 1 },
    { _id: 2, host: "shard3-arbiter:29019", arbiterOnly: true }
  ]
})'

# Step 3: Add shard to cluster
mongosh mongodb://mongos:27017/admin --eval '
sh.addShard("shard3rs/shard3-primary:29019,shard3-secondary:29019")'

# Step 4: Verify
sh.status()
```

### 10.2 Removing a Shard

```javascript
// Step 1: Start draining
use admin
db.adminCommand({ removeShard: "shard2rs" })

// Step 2: Monitor progress (repeat until complete)
db.adminCommand({ removeShard: "shard2rs" })
// Returns: { state: "ongoing", remaining: { chunks: N, dbs: N } }

// Step 3: Move primary databases off shard
db.adminCommand({ movePrimary: "tenant_db", to: "shard1rs" })

// Step 4: Wait for completion
// Returns: { state: "completed" }

// Step 5: Remove Docker service
docker service rm mongo_shard2_repl
```

### 10.3 Balancer Management

```javascript
// Check balancer status
sh.getBalancerState()
sh.isBalancerRunning()

// Stop balancer (for maintenance)
sh.stopBalancer()

// Start balancer
sh.startBalancer()

// Configure balancing window (avoid peak hours)
use config
db.settings.updateOne(
   { _id: "balancer" },
   { $set: {
       activeWindow: { start: "02:00", stop: "06:00" },
       _secondaryThrottle: true
   }},
   { upsert: true }
)
```

### 10.4 Backup Procedures

```bash
# Mongodump from mongos (consistent backup)
mongodump \
  --uri="mongodb://root:password@mongos:27017" \
  --authenticationDatabase=admin \
  --oplog \
  --out=/backup/$(date +%Y%m%d)

# Per-shard backup (for large clusters)
for shard in shard1rs shard2rs shard3rs; do
  mongodump \
    --uri="mongodb://root:password@${shard}-primary:29017" \
    --authenticationDatabase=admin \
    --oplog \
    --out=/backup/$(date +%Y%m%d)/${shard}
done

# Config server backup
mongodump \
  --uri="mongodb://root:password@config1:28017" \
  --authenticationDatabase=admin \
  --out=/backup/$(date +%Y%m%d)/config
```

---

## 11. Monitoring and Alerting

### 11.1 Key Metrics

**Cluster Health**:
```javascript
// Shard status
sh.status()

// Replica set status
rs.status()

// Current operations
db.currentOp()

// Server statistics
db.serverStatus()
```

**Performance Metrics**:
| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| `opcounters.query` | serverStatus | > 10000/s |
| `opcounters.insert` | serverStatus | > 5000/s |
| `connections.current` | serverStatus | > 80% of available |
| `repl.lag` | rs.status() | > 10 seconds |
| `chunks.imbalance` | sh.status() | > 20% difference |
| `storage.dataSize` | collStats | > 80% allocated |

### 11.2 Monitoring Integration

**InfluxDB/Telegraf Configuration** (from `zona_services/custom_telegraf/`):
```toml
[[inputs.mongodb]]
  servers = ["mongodb://root:password@mongos:27017/admin"]
  gather_perdb_stats = true
  gather_col_stats = true
  col_stats_dbs = ["fkart_incidents"]

[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${INFLUXDB_TOKEN}"
  organization = "securaa"
  bucket = "stats"
```

### 11.3 Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: mongodb_sharding
    rules:
      - alert: MongoDBReplicaSetLag
        expr: mongodb_rs_members_replicationLag > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "MongoDB replica lag detected"

      - alert: MongoDBShardImbalance
        expr: abs(mongodb_shard_chunks - avg(mongodb_shard_chunks)) > 100
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "MongoDB shard chunk imbalance"

      - alert: MongoDBHighConnections
        expr: mongodb_connections_current / mongodb_connections_available > 0.8
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "MongoDB connection pool near exhaustion"
```

---

## 12. Disaster Recovery

### 12.1 Recovery Scenarios

**Scenario 1: Single Shard Primary Failure**
```bash
# Automatic failover via replica set election
# Monitor: rs.status() on affected shard
# Recovery time: 10-30 seconds (election timeout)
```

**Scenario 2: Entire Shard Failure**
```bash
# 1. Stop queries to affected shard
sh.disableBalancing("fkart_incidents.zona_incidents")

# 2. Restore from backup to new nodes
mongorestore --uri="mongodb://new-shard-primary:29017" /backup/shardXrs

# 3. Reconfigure replica set
rs.reconfig({ ... new members ... })

# 4. Re-add to cluster
sh.addShard("shardXrs/new-primary:29017")

# 5. Re-enable balancing
sh.enableBalancing("fkart_incidents.zona_incidents")
```

**Scenario 3: Config Server Failure**
```bash
# Config servers use replica set - automatic failover
# If majority lost:
# 1. Restore config database from backup
# 2. Reconfigure replica set
# WARNING: Cluster operations blocked until config servers available
```

### 12.2 Backup/Restore Strategy

| Component | Backup Frequency | Retention | Method |
|-----------|------------------|-----------|--------|
| Config Servers | Every 6 hours | 7 days | mongodump with oplog |
| Shards | Daily full, hourly incremental | 30 days | Filesystem snapshots |
| Meta DB | Every 6 hours | 7 days | mongodump |

### 12.3 RPO/RTO Targets

| Scenario | RPO | RTO |
|----------|-----|-----|
| Single node failure | 0 (replication) | < 30 seconds |
| Shard failure | < 1 hour | < 4 hours |
| Complete cluster failure | < 24 hours | < 8 hours |
| Region failure (DR) | < 24 hours | < 24 hours |

---

## Appendix A: Collection Reference

### Complete Collection List (from `securaa_lib/config/server.go`)

```
Core Collections:
├── tenants                    # Tenant management (MSSP)
├── users                      # User accounts
├── roles                      # Permission roles
├── user_session               # Active sessions
├── user_groups                # User grouping

Case Management:
├── zona_incidents             # Security incidents/cases (HIGH VOLUME)
├── incident_categories        # Case categorization
├── incident_status            # Status definitions
├── incident_severities        # Severity levels
├── investigation              # Investigation records
├── casegroup                  # Case grouping

Automation:
├── playbooks                  # Playbook definitions
├── playbooks_executions       # Execution history (HIGH VOLUME)
├── tasks                      # Task definitions
├── task_execution             # Task execution logs (HIGH VOLUME)
├── pre_process_rules          # Pre-processing rules
├── approvals                  # Approval workflows

Integration:
├── integration                # Integration catalog
├── active_instance            # Active integration instances
├── feeds                      # Threat intelligence feeds

Audit & Logging:
├── auditCollection            # Audit trail (HIGH VOLUME)
├── zona_loginfo               # System logs

Configuration:
├── system                     # System settings
├── securaa_license            # License information
├── current_release            # Version info
├── sla                        # SLA definitions
├── shifts                     # Shift management

Reports & Dashboards:
├── reports                    # Report definitions
├── report_collection          # Report data
├── custom_dashboard           # Dashboard configs
├── zona_widgets               # Widget definitions
```

---

## Appendix B: Docker Image Tags

| Image | Tag | Purpose |
|-------|-----|---------|
| `custom_mongodb_shard` | `mongo_7.0` | Shard server with auth |
| `custom_mongodb_shard` | `mongo_noauth_7.0` | Shard server initial setup |
| `custom_mongos` | `mongo_7.0` | Query router |
| `custom_mongodb_replica` | `mongoreplic_7.0` | Standard replica set |
| `custom_mongodb_replica_incremental` | `release_repl_incremental` | Incremental backup support |

---

## Appendix C: Port Reference

| Port | Service | Description |
|------|---------|-------------|
| 27017 | Mongos | Application connection |
| 27018 | Meta DB | Sharding metadata |
| 28017 | Config Server | Cluster configuration |
| 29017 | Shard 1 | First data shard |
| 29018 | Shard 2 | Second data shard |
| 29019-29066 | Shards 3-50 | Additional shards |
| 8253 | Shard Handler | Shard management API |
| 8251 | Arbiter Handler | Arbiter management API |
| 8250 | Health Check | Primary server health |

---

## Appendix D: Troubleshooting

### Common Issues

**Issue: Shard not accepting writes**
```javascript
// Check if shard is primary
rs.isMaster()

// Check replication status
rs.status()

// Force reconfiguration if needed
rs.reconfig(rs.conf(), {force: true})
```

**Issue: Slow queries**
```javascript
// Enable profiler
db.setProfilingLevel(1, { slowms: 100 })

// Analyze slow queries
db.system.profile.find().sort({ ts: -1 }).limit(10)

// Check explain plan
db.zona_incidents.find({ tenantcode: "x" }).explain("executionStats")
```

**Issue: Chunk migration stuck**
```javascript
// Check migration status
use config
db.locks.find({ _id: "balancer" })

// Abort stuck migration
db.adminCommand({ balancerStop: 1 })
db.locks.remove({ _id: "balancer" })
db.adminCommand({ balancerStart: 1 })
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 2024 | System Architect | Initial comprehensive architecture |

---

*This document is auto-generated based on codebase analysis and should be reviewed by the infrastructure team before implementation.*
