# Zona Custom Utils Service - High-Level Design (HLD)

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Business Requirements](#business-requirements)
4. [Solution Architecture](#solution-architecture)
5. [Component Architecture](#component-architecture)
6. [Data Architecture](#data-architecture)
7. [Security Architecture](#security-architecture)
8. [Performance Architecture](#performance-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [Integration Architecture](#integration-architecture)
11. [Business Process Flows](#business-process-flows)
12. [Non-Functional Requirements](#non-functional-requirements)

## Executive Summary

The Zona Custom Utils Service is a microservice designed to enable users to create, manage, and execute custom utility functions in a secure, multi-tenant environment. The service supports Python-based transformers and scripts, providing isolated execution environments through containerization while maintaining comprehensive audit trails and performance optimization.

### Key Business Value
- **Extensibility**: Allows users to create custom data processing utilities
- **Security**: Provides secure code validation and isolated execution
- **Multi-tenancy**: Supports multiple tenants with data isolation
- **Scalability**: Designed for high-volume, concurrent operations
- **Compliance**: Comprehensive audit logging for regulatory requirements

### Solution Approach
- **Microservice Architecture**: Self-contained service with clear boundaries
- **Container-based Execution**: Docker containers for secure Python code execution
- **Multi-tier Caching**: Redis and in-memory caching for performance
- **Multi-tenant Data Model**: Isolated data storage per tenant
- **Event-driven Processing**: Asynchronous operations for non-critical tasks

## System Overview

```mermaid
graph TB
    subgraph "External Interfaces"
        WEB[Web UI]
        API[REST API Clients]
        MOBILE[Mobile Apps]
    end
    
    subgraph "API Gateway Layer"
        LB[Load Balancer]
        SSL[SSL Termination]
        AUTH[Authentication Gateway]
    end
    
    subgraph "Zona Custom Utils Service"
        APP[Application Layer]
        BL[Business Logic Layer]
        DATA[Data Access Layer]
        INFRA[Infrastructure Layer]
    end
    
    subgraph "Data Storage"
        MONGO[(MongoDB Cluster)]
        REDIS[(Redis Cluster)]
        FS[File System Storage]
    end
    
    subgraph "External Services"
        DOCKER[Docker Engine]
        LOGGING[Logging Service]
        MONITORING[Monitoring Service]
    end
    
    WEB --> LB
    API --> LB
    MOBILE --> LB
    
    LB --> SSL
    SSL --> AUTH
    AUTH --> APP
    
    APP --> BL
    BL --> DATA
    DATA --> INFRA
    
    DATA --> MONGO
    DATA --> REDIS
    INFRA --> FS
    INFRA --> DOCKER
    
    APP --> LOGGING
    APP --> MONITORING
```

### System Context
The Zona Custom Utils Service operates within a larger ecosystem of microservices, providing custom utility management capabilities. It integrates with:

- **Authentication Services**: For user authentication and authorization
- **Tenant Management**: For multi-tenant configuration and isolation
- **Container Orchestration**: For isolated execution environments
- **Monitoring Infrastructure**: For observability and alerting
- **Storage Services**: For persistent data and file management

## Business Requirements

### Functional Requirements

#### FR-001: Custom Utility Management
- Users must be able to create custom Python utilities
- System must validate Python syntax and security
- Users must be able to update existing utilities
- Users must be able to delete utilities they own
- System must maintain version history

#### FR-002: Code Validation and Security
- System must validate Python syntax before saving
- System must scan for prohibited code patterns
- System must prevent execution of malicious code
- System must provide detailed validation feedback

#### FR-003: Utility Execution
- Users must be able to execute their custom utilities
- System must provide real-time execution output
- System must support parameterized execution
- System must handle execution timeouts gracefully

#### FR-004: Multi-tenant Support
- System must isolate data between tenants
- System must support tenant-specific configurations
- System must enable cross-tenant utility copying
- System must maintain tenant-level audit trails

#### FR-005: Export/Import Functionality
- Users must be able to export utilities
- Users must be able to import utilities
- System must support bulk operations
- System must validate imported utilities

#### FR-006: Audit and Compliance
- System must log all user actions
- System must maintain execution history
- System must provide compliance reporting
- System must support data retention policies

### Non-Functional Requirements

#### NFR-001: Performance
- API response time < 500ms for read operations
- API response time < 2s for write operations
- System must support 1000+ concurrent users
- Utility execution timeout < 300 seconds

#### NFR-002: Scalability
- System must scale horizontally
- Must support 100+ tenants
- Must handle 10,000+ utilities per tenant
- Database must support sharding

#### NFR-003: Availability
- System uptime > 99.9%
- Recovery time < 5 minutes
- Data backup every 24 hours
- Multi-region disaster recovery

#### NFR-004: Security
- All data encrypted at rest and in transit
- Role-based access control
- Code execution in isolated environments
- Regular security audits

#### NFR-005: Usability
- Intuitive web interface
- Comprehensive API documentation
- Real-time feedback and validation
- Multi-language support

## Solution Architecture

### Architectural Principles
1. **Single Responsibility**: Each component has a well-defined purpose
2. **Loose Coupling**: Components interact through well-defined interfaces
3. **High Cohesion**: Related functionality is grouped together
4. **Separation of Concerns**: Clear boundaries between different aspects
5. **Fail-Safe Design**: Graceful degradation under failure conditions

### Architecture Patterns
- **Layered Architecture**: Clear separation between presentation, business, and data layers
- **Repository Pattern**: Abstracted data access layer
- **Builder Pattern**: Complex object construction
- **Middleware Pattern**: Cross-cutting concerns handling
- **Circuit Breaker**: Fault tolerance for external service calls

### Technology Decisions

#### Programming Language: Go
**Rationale**: 
- High performance and low latency
- Excellent concurrency support
- Strong ecosystem for microservices
- Easy deployment and maintenance

#### Database: MongoDB
**Rationale**:
- Document-based model fits utility metadata
- Horizontal scaling capabilities
- Rich querying capabilities
- Multi-tenant support

#### Cache: Redis
**Rationale**:
- High-performance in-memory storage
- Advanced data structures
- Pub/Sub capabilities
- Clustering support

#### Container Runtime: Docker
**Rationale**:
- Isolated execution environment
- Resource management
- Portability across environments
- Extensive ecosystem

## Component Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        HTTP[HTTP Router]
        MIDDLEWARE[Middleware Stack]
        CONTROLLERS[Controllers]
    end
    
    subgraph "Business Logic Layer"
        SERVICES[Services]
        BUILDERS[Builders]
        VALIDATORS[Validators]
    end
    
    subgraph "Data Access Layer"
        REPOSITORIES[Repositories]
        MODELS[Data Models]
        CACHE[Cache Layer]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER_MGR[Container Manager]
        FILE_MGR[File Manager]
        AUDIT[Audit Logger]
        METRICS[Metrics Collector]
    end
    
    HTTP --> MIDDLEWARE
    MIDDLEWARE --> CONTROLLERS
    CONTROLLERS --> SERVICES
    SERVICES --> BUILDERS
    SERVICES --> VALIDATORS
    SERVICES --> REPOSITORIES
    REPOSITORIES --> MODELS
    REPOSITORIES --> CACHE
    SERVICES --> DOCKER_MGR
    SERVICES --> FILE_MGR
    SERVICES --> AUDIT
    SERVICES --> METRICS
```

### Component Responsibilities

#### Presentation Layer
- **HTTP Router**: Route incoming requests to appropriate controllers
- **Middleware Stack**: Handle authentication, logging, and cross-cutting concerns
- **Controllers**: Process HTTP requests and generate responses

#### Business Logic Layer
- **Services**: Implement core business logic and orchestrate operations
- **Builders**: Construct complex objects and configurations
- **Validators**: Validate input data and business rules

#### Data Access Layer
- **Repositories**: Abstract data access operations
- **Data Models**: Define data structures and relationships
- **Cache Layer**: Provide high-performance data access

#### Infrastructure Layer
- **Container Manager**: Manage Docker container lifecycle
- **File Manager**: Handle file system operations
- **Audit Logger**: Record audit trails and compliance data
- **Metrics Collector**: Gather performance and operational metrics

## Data Architecture

### Logical Data Model

```mermaid
erDiagram
    TENANT {
        int id PK
        string tenantcode UK
        string name
        string status
        string db_host
        string connection_status
    }
    
    CUSTOM_UTIL {
        int id PK
        string name UK
        string tenantcode FK
        int userid FK
        string description
        string status
        string category
        text filecontents
        bigint createddate
        bigint updateddate
        text input_params
        text output_fields
        array playbook_names
    }
    
    TASK_EXECUTION {
        string id PK
        int taskid FK
        int userid FK
        string tenantcode FK
        bigint createddate
        text request
        text response
        string status
        float execution_time
    }
    
    AUDIT_LOG {
        string id PK
        string tenantcode FK
        int userid FK
        string action
        string resource
        bigint timestamp
        text details
    }
    
    TENANT ||--o{ CUSTOM_UTIL : contains
    CUSTOM_UTIL ||--o{ TASK_EXECUTION : executes
    TENANT ||--o{ AUDIT_LOG : generates
```

### Data Storage Strategy

#### Primary Data Storage (MongoDB)
- **Collections**: Utilities, executions, audit logs, tenants
- **Sharding Strategy**: Shard by tenant code for horizontal scaling
- **Replica Sets**: 3-node replica sets for high availability
- **Backup Strategy**: Daily backups with point-in-time recovery

#### Cache Strategy (Redis)
- **L1 Cache**: Application-level caching (5 minutes TTL)
- **L2 Cache**: Redis caching (1 hour TTL)
- **Cache Keys**: Hierarchical naming convention
- **Eviction Policy**: LRU with memory limit enforcement

#### File Storage
- **Code Files**: Encrypted Python files on network storage
- **Logs**: Execution logs on distributed file system
- **Backups**: Compressed archives on object storage

### Data Security
- **Encryption at Rest**: AES-256 encryption for all stored data
- **Encryption in Transit**: TLS 1.3 for all network communication
- **Data Masking**: Sensitive data masked in logs and non-production environments
- **Access Control**: Role-based access with principle of least privilege

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Perimeter Security"
        WAF[Web Application Firewall]
        DDOS[DDoS Protection]
        FIREWALL[Network Firewall]
    end
    
    subgraph "Application Security"
        AUTH[Authentication]
        AUTHZ[Authorization]
        INPUT_VAL[Input Validation]
        CODE_SCAN[Code Scanning]
    end
    
    subgraph "Data Security"
        ENCRYPT[Data Encryption]
        MASKING[Data Masking]
        BACKUP_SEC[Secure Backup]
    end
    
    subgraph "Runtime Security"
        CONTAINER_SEC[Container Security]
        ISOLATION[Process Isolation]
        MONITORING[Security Monitoring]
    end
    
    WAF --> DDOS
    DDOS --> FIREWALL
    FIREWALL --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> INPUT_VAL
    INPUT_VAL --> CODE_SCAN
    CODE_SCAN --> ENCRYPT
    ENCRYPT --> MASKING
    MASKING --> BACKUP_SEC
    BACKUP_SEC --> CONTAINER_SEC
    CONTAINER_SEC --> ISOLATION
    ISOLATION --> MONITORING
```

### Authentication and Authorization

#### Authentication Flow
1. User provides credentials to authentication service
2. Authentication service validates credentials
3. JWT token issued with user claims and permissions
4. Token included in subsequent API requests
5. Service validates token and extracts user context

#### Authorization Model
- **Role-Based Access Control (RBAC)**
- **Tenant-based isolation**
- **Resource-level permissions**
- **Operation-level granularity**

#### Permission Matrix
| Role | Create Utils | Read Utils | Execute Utils | Delete Utils | Admin Functions |
|------|--------------|------------|---------------|--------------|-----------------|
| User | Own | Own | Own | No | No |
| Creator | Own | Own | Own | Own | No |
| Admin | All | All | All | All | Limited |
| Super Admin | All | All | All | All | All |

### Code Security

#### Validation Rules
- **Syntax Validation**: Python AST parsing
- **Security Scanning**: Pattern-based security checks
- **Dependency Analysis**: Package security assessment
- **Resource Limits**: Memory and CPU constraints

#### Prohibited Patterns
- File system access (`open()`, `file()`)
- Network operations (`socket`, `urllib`, `requests`)
- Process execution (`subprocess`, `os.system`)
- System imports (`os`, `sys`, `subprocess`)

## Performance Architecture

### Performance Strategy

```mermaid
graph TD
    REQUEST[Incoming Request] --> CACHE_L1{L1 Cache}
    CACHE_L1 -->|Hit| RETURN_FAST[Return Cached]
    CACHE_L1 -->|Miss| CACHE_L2{L2 Cache}
    CACHE_L2 -->|Hit| UPDATE_L1[Update L1]
    CACHE_L2 -->|Miss| DATABASE[Database Query]
    UPDATE_L1 --> RETURN_FAST
    DATABASE --> OPTIMIZE{Optimized Query?}
    OPTIMIZE -->|Yes| FAST_QUERY[Execute Fast Query]
    OPTIMIZE -->|No| SLOW_QUERY[Execute Slow Query]
    FAST_QUERY --> CACHE_UPDATE[Update Caches]
    SLOW_QUERY --> CACHE_UPDATE
    CACHE_UPDATE --> RETURN_RESULT[Return Result]
```

### Performance Targets

#### Response Time Requirements
| Operation | Target | Maximum |
|-----------|--------|---------|
| Get Utility List | < 200ms | 500ms |
| Create Utility | < 1s | 2s |
| Validate Code | < 500ms | 1s |
| Execute Utility | < 10s | 300s |
| Export/Import | < 5s | 30s |

#### Throughput Requirements
| Metric | Target | Peak |
|--------|--------|------|
| Requests/Second | 1000 | 5000 |
| Concurrent Users | 100 | 500 |
| Utility Executions/Minute | 60 | 300 |

### Optimization Strategies

#### Database Optimization
- **Indexing Strategy**: Compound indexes for common query patterns
- **Query Optimization**: Aggregation pipelines for complex queries
- **Connection Pooling**: Reuse database connections
- **Read Replicas**: Distribute read load across replicas

#### Caching Strategy
- **Multi-level Caching**: Application, Redis, and database caching
- **Cache Warming**: Pre-populate frequently accessed data
- **Cache Invalidation**: Event-driven cache updates
- **Cache Partitioning**: Distribute cache load

#### Application Optimization
- **Goroutine Pooling**: Reuse goroutines for concurrent operations
- **Memory Management**: Efficient memory allocation and garbage collection
- **Compression**: Compress large responses
- **Connection Reuse**: HTTP connection pooling

## Deployment Architecture

### Production Environment

```mermaid
graph TB
    subgraph "Load Balancer Tier"
        LB1[Load Balancer 1]
        LB2[Load Balancer 2]
    end
    
    subgraph "Application Tier"
        APP1[App Instance 1]
        APP2[App Instance 2]
        APP3[App Instance 3]
    end
    
    subgraph "Data Tier"
        MONGO_P[MongoDB Primary]
        MONGO_S1[MongoDB Secondary 1]
        MONGO_S2[MongoDB Secondary 2]
        REDIS_M[Redis Master]
        REDIS_S[Redis Slave]
    end
    
    subgraph "Container Tier"
        DOCKER1[Docker Host 1]
        DOCKER2[Docker Host 2]
        DOCKER3[Docker Host 3]
    end
    
    INTERNET[Internet] --> LB1
    INTERNET --> LB2
    LB1 --> APP1
    LB1 --> APP2
    LB2 --> APP2
    LB2 --> APP3
    APP1 --> MONGO_P
    APP2 --> MONGO_P
    APP3 --> MONGO_P
    MONGO_P --> MONGO_S1
    MONGO_P --> MONGO_S2
    APP1 --> REDIS_M
    APP2 --> REDIS_M
    APP3 --> REDIS_M
    REDIS_M --> REDIS_S
    APP1 --> DOCKER1
    APP2 --> DOCKER2
    APP3 --> DOCKER3
```

### Deployment Strategy
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rolling Updates**: Gradual rollout of new versions
- **Canary Releases**: Limited exposure testing
- **Automated Rollback**: Quick recovery from failed deployments

### Environment Management
- **Development**: Single instance for development and testing
- **Staging**: Production-like environment for validation
- **Production**: High-availability multi-instance deployment
- **Disaster Recovery**: Secondary region for business continuity

## Integration Architecture

### External Service Integration

```mermaid
graph LR
    subgraph "Zona Custom Utils"
        CORE[Core Service]
    end
    
    subgraph "Internal Services"
        AUTH_SVC[Authentication Service]
        TENANT_SVC[Tenant Management]
        AUDIT_SVC[Audit Service]
        NOTIFY_SVC[Notification Service]
    end
    
    subgraph "External Services"
        DOCKER_API[Docker Engine API]
        FILE_STORAGE[File Storage Service]
        MONITORING[Monitoring Service]
        LOGGING[Logging Service]
    end
    
    CORE <--> AUTH_SVC
    CORE <--> TENANT_SVC
    CORE --> AUDIT_SVC
    CORE --> NOTIFY_SVC
    CORE <--> DOCKER_API
    CORE <--> FILE_STORAGE
    CORE --> MONITORING
    CORE --> LOGGING
```

### Integration Patterns

#### Synchronous Integration
- **REST API**: For real-time operations requiring immediate response
- **Direct Database Access**: For high-performance data operations
- **File System Access**: For code storage and retrieval

#### Asynchronous Integration
- **Event Publishing**: For audit logging and notifications
- **Message Queues**: For long-running operations
- **Batch Processing**: For bulk operations and maintenance tasks

## Business Process Flows

### Custom Utility Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant Service
    participant Validator
    participant Storage
    participant Docker
    
    User->>UI: Create Utility
    UI->>API: POST /custom-utils
    API->>Service: Process Request
    Service->>Validator: Validate Code
    Validator->>Service: Validation Results
    
    alt Validation Failed
        Service->>API: Error Response
        API->>UI: Validation Errors
        UI->>User: Show Errors
    else Validation Passed
        Service->>Storage: Save Utility
        Service->>Docker: Update Config
        Service->>API: Success Response
        API->>UI: Confirmation
        UI->>User: Success Message
    end
```

### Utility Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant Service
    participant Container
    participant Storage
    
    User->>UI: Execute Utility
    UI->>API: POST /execute
    API->>Service: Execute Request
    Service->>Container: Start Execution
    Container->>Container: Run Python Code
    Container->>Service: Stream Output
    Service->>API: Real-time Results
    API->>UI: Stream Response
    UI->>User: Show Output
    Container->>Service: Final Results
    Service->>Storage: Store Results
    Service->>API: Completion
    API->>UI: Execution Complete
```

### Multi-Tenant Deployment Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Service
    participant MasterDB
    participant TenantDB
    participant Cache
    
    Admin->>Service: Deploy to New Tenant
    Service->>MasterDB: Get Source Utilities
    Service->>Service: Process Utilities
    
    loop For Each Utility
        Service->>TenantDB: Create Utility
        Service->>Cache: Clear Cache
        Service->>Service: Update Metadata
    end
    
    Service->>Admin: Deployment Complete
```

## Non-Functional Requirements

### Availability Requirements
- **Uptime Target**: 99.9% (8.76 hours downtime per year)
- **Planned Maintenance**: Maximum 4 hours per month
- **Recovery Time Objective (RTO)**: 15 minutes
- **Recovery Point Objective (RPO)**: 1 hour

### Scalability Requirements
- **Horizontal Scaling**: Auto-scaling based on load
- **Vertical Scaling**: Resource scaling for individual instances
- **Database Scaling**: Sharding and read replicas
- **Cache Scaling**: Redis clustering for distributed caching

### Reliability Requirements
- **Mean Time Between Failures (MTBF)**: > 720 hours
- **Mean Time To Recovery (MTTR)**: < 15 minutes
- **Error Rate**: < 0.1% for API requests
- **Data Consistency**: Eventual consistency for non-critical data

### Maintainability Requirements
- **Code Coverage**: > 80% for unit tests
- **Documentation**: Comprehensive API and architecture documentation
- **Monitoring**: Full observability with metrics, logs, and traces
- **Deployment**: Automated CI/CD pipeline with rollback capability

### Compliance Requirements
- **Data Privacy**: GDPR and CCPA compliance
- **Security Standards**: SOC 2 Type II certification
- **Audit Logging**: Complete audit trail for all operations
- **Data Retention**: Configurable retention policies per tenant

---

*This High-Level Design document provides a comprehensive overview of the Zona Custom Utils Service architecture, focusing on business requirements, solution approach, and architectural decisions. It serves as a foundation for detailed technical implementation and stakeholder communication.*