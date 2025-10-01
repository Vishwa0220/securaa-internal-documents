# Securaa SIEM Service - High-Level Design Document

## 1. Executive Summary

The **Securaa SIEM (Security Information and Event Management)** service is a comprehensive, multi-tenant security platform designed to collect, process, analyze, and manage security incidents and events. It provides APIs for incident management, case handling, dashboard analytics, playbook automation, and integrations with external SIEM tools.

---

## 2. System Architecture Overview

```mermaid
graph TB
    subgraph "External Systems"
        EXT1[QRadar]
        EXT2[Azure Sentinel]
        EXT3[Securonix]
        EXT4[BluSapphire]
        EXT5[ElasticSearch]
        EXT6[ServiceNow]
    end
    subgraph "Securaa SIEM Service (Port 8003)"
        subgraph "API Layer"
            API[REST API Endpoints]
            MW[Middleware<br/>Authentication/Authorization]
        end
        subgraph "Controller Layer"
            IC[Incidents Controller]
            CC[Category Controller]
            UC[User Controller]
            DC[Dashboard Controller]
            PC[Playbook Controller]
            MC[Monitoring Controller]
            WC[Widget Controller]
        end
        subgraph "Service Layer"
            IS[Incident Services]
            CS[Case Services]
            DS[Dashboard Services]
            MS[Monitoring Services]
            AS[Analytics Services]
        end
        subgraph "Data Layer"
            MOD[Models/DTOs]
            HELP[Helpers & Utils]
        end
    end
    subgraph "Infrastructure"
        MONGO[(MongoDB)]
        INFLUX[(InfluxDB)]
        REDIS[(Redis Cache)]
        FILE[File System]
    end
    subgraph "Client Applications"
        WEB[Web Dashboard]
        API_CLIENT[API Clients]
    end
    EXT1 --> API
    EXT2 --> API
    EXT3 --> API
    EXT4 --> API
    EXT5 --> API
    EXT6 --> API
    WEB --> API
    API_CLIENT --> API
    API --> MW
    MW --> IC
    MW --> CC
    MW --> UC
    MW --> DC
    MW --> PC
    MW --> MC
    MW --> WC
    IC --> IS
    CC --> CS
    UC --> DS
    DC --> MS
    PC --> AS
    MC --> IS
    WC --> CS
    
    IS --> MOD
    CS --> MOD
    DS --> MOD
    MS --> MOD
    AS --> MOD
    MOD --> HELP
    HELP --> MONGO
    HELP --> INFLUX
    HELP --> REDIS
    HELP --> FILE
```

---

## 3. Detailed Component Architecture

### 3.1 Application Structure

```mermaid
graph TD
    subgraph "Securaa SIEM Directory Structure"
        APP[app.go - Main Application]
        MAIN[main.go - Entry Point]
        subgraph "Controllers"
            CTRL1[IncidentsController.go]
            CTRL2[categoryController.go]
            CTRL3[dashboardController.go]
            CTRL4[playbookController.go]
            CTRL5[monitoringController.go]
            CTRL6[widgetController.go]
            CTRL7[+ 25 more controllers]
        end
        subgraph "Models"
            MOD1[Incidents.go]
            MOD2[CaseGroup.go]
            MOD3[category.go]
            MOD4[investigation.go]
            MOD5[Response.go]
            MOD6[+ 15 more models]
        end
        subgraph "Services"
            SRV1[service.go]
            SRV2[caseMirroringService.go]
            SRV3[monitoringDashboardServices.go]
            SRV4[uniqueservices.go]
        end
        
        subgraph "Helpers & Utils"
            HELP1[caseMirroringHelpers.go]
            UTIL1[mitre.go]
            UTIL2[monitoringDashboardSupport.go]
        end
        subgraph "Constants"
            CONST[constants.go]
        end
    end
    MAIN --> APP
    APP --> CTRL1
    APP --> CTRL2
    APP --> CTRL3
    CTRL1 --> MOD1
    CTRL2 --> MOD2
    CTRL3 --> MOD3
    MOD1 --> SRV1
    SRV1 --> HELP1
    HELP1 --> CONST
```

### 3.2 Data Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Middleware
    participant Controller
    participant Service
    participant Model
    participant Database
    Client->>API: HTTP Request
    API->>Middleware: Route to Middleware
    Middleware->>Middleware: Authentication/Authorization
    Middleware->>Middleware: Session Management
    Middleware->>Controller: Forward Request
    Controller->>Controller: Input Validation
    Controller->>Service: Business Logic Call
    Service->>Service: Process Business Rules
    Service->>Model: Data Operation
    Model->>Database: CRUD Operations
    Database-->>Model: Result Set
    Model-->>Service: Processed Data
    Service-->>Controller: Business Result
    Controller->>Controller: Format Response
    Controller-->>API: JSON Response
    API-->>Client: HTTP Response
```

---

## 4. Core Features & Capabilities

### 4.1 Incident Management
- **Incident CRUD Operations**: Create, Read, Update, Delete incidents
- **Incident Status Management**: Open, In Progress, Closed, Escalated
- **Incident Assignment**: Assign to analysts/teams
- **Incident Categorization**: Security categories and severity levels
- **Incident Timeline**: Track all actions and changes
- **Bulk Operations**: Update/delete multiple incidents

### 4.2 Case Management
- **Case Grouping**: Group related incidents into cases
- **Case Mirroring**: Synchronize cases across tenants
- **Case Workflow**: Define case lifecycle and approval processes
- **Case Analytics**: Generate insights from case data
- **Case Export**: Download case data in various formats

### 4.3 Dashboard & Analytics
- **Real-time Dashboards**: Live security metrics and KPIs
- **Custom Widgets**: Configurable dashboard components
- **Trend Analysis**: Historical data analysis and forecasting
- **Geographic Analysis**: Location-based threat visualization
- **MITRE ATT&CK Mapping**: Threat technique classification

### 4.4 Integration & Data Sources
- **SIEM Tool Integration**: QRadar, Splunk, Azure Sentinel, etc.
- **Ticketing System Integration**: ServiceNow, Jira
- **Threat Intelligence**: External threat feed integration
- **API Gateway**: RESTful APIs for third-party integrations

### 4.5 Multi-Tenant Architecture
- **Tenant Isolation**: Complete data separation between tenants
- **Tenant-specific Configuration**: Custom settings per tenant
- **Cross-tenant Analytics**: Master tenant view capabilities
- **Tenant Onboarding**: Automated tenant setup and configuration

---

## 5. Database Design

### 5.1 Core Collections/Tables

```mermaid
erDiagram
    INCIDENTS ||--o{ INVESTIGATIONS : has
    INCIDENTS ||--o{ TIMELINE : contains
    INCIDENTS }o--|| CATEGORIES : belongs_to
    INCIDENTS }o--|| SEVERITY : has
    INCIDENTS }o--|| USERS : assigned_to
    
    CASES ||--o{ INCIDENTS : groups
    CASES ||--o{ CASE_GROUPS : belongs_to
    
    TENANTS ||--o{ INCIDENTS : owns
    TENANTS ||--o{ USERS : contains
    TENANTS ||--o{ CATEGORIES : defines
    
    PLAYBOOKS ||--o{ TASKS : contains
    PLAYBOOKS }o--|| INCIDENTS : executed_on
    
    INCIDENTS {
        string securaa_s_incident_id PK
        string description
        string securaa_s_status
        string securaa_s_severity
        int securaa_s_assigned_to FK
        int securaa_s_category_id FK
        timestamp securaa_s_createdts
        timestamp securaa_s_updatedts
        array securaa_s_source_ips
        array securaa_s_destination_ips
        object securaa_s_timeline
        string securaa_s_source
        bool securaa_s_is_confirmed
    }
    
    CASES {
        string case_id PK
        string case_name
        string case_status
        string case_priority
        array incident_ids
        int assigned_analyst FK
        timestamp created_date
        timestamp updated_date
        string tenant_code FK
    }
    
    CATEGORIES {
        int category_id PK
        string category_name
        string description
        string tenant_code FK
        bool is_active
        timestamp created_date
    }
    
    USERS {
        int user_id PK
        string username
        string email
        string role
        string tenant_code FK
        bool is_active
        timestamp last_login
    }
    
    TENANTS {
        string tenant_code PK
        string tenant_name
        string db_host
        string connection_status
        object configuration
        timestamp created_date
    }
```

### 5.2 Key Data Models

#### SecuraaOffenses (Main Incident Model)
```go
type SecuraaOffenses struct {
    SecuraaSIncidentID           int                `json:"securaa_s_incident_id"`
    SecuraaDescription           string             `json:"description"`
    SecuraaSStatus              string             `json:"securaa_s_status"`
    SecuraaSSeverity            string             `json:"securaa_s_severity"`
    SecuraaSAssignedTo          int                `json:"securaa_s_assigned_to"`
    SecuraaScategoryID          int                `json:"securaa_s_category_id"`
    SecuraaSTimeline            []IncidentTimeLine `json:"securaa_s_timeline"`
    SecuraaSSourceIPs           []string           `json:"securaa_s_source_ips"`
    SecuraaSDestinationIPs      []string           `json:"securaa_s_destination_ips"`
    SecuraaSCreatedts           int64              `json:"securaa_s_createdts"`
    SecuraaSUpdatedts           int64              `json:"securaa_s_updatedts"`
    // ... additional fields
}
```

#### CaseGrouping Model
```go
type CaseGrouping struct {
    CaseID          string    `json:"case_id"`
    CaseName        string    `json:"case_name"`
    CaseStatus      string    `json:"case_status"`
    CasePriority    string    `json:"case_priority"`
    IncidentIDs     []string  `json:"incident_ids"`
    AssignedAnalyst int       `json:"assigned_analyst"`
    TenantCode      string    `json:"tenant_code"`
    CreatedDate     time.Time `json:"created_date"`
}
```

---

## 6. API Design

### 6.1 Core API Categories

```mermaid
graph LR
    subgraph "Securaa SIEM APIs"
        subgraph "Incident APIs"
            I1[GET /securaaincidentslist]
            I2[GET /securaaincident/{id}]
            I3[POST /securaaincident]
            I4[PUT /securaaincident]
            I5[DELETE /deletemultipleincidents]
        end
        
        subgraph "Case APIs"
            C1[GET /getalltenantscases]
            C2[POST /createcasegroup]
            C3[PUT /updatecasestatus]
            C4[GET /getcasescount]
        end
        
        subgraph "Dashboard APIs"
            D1[GET /getmeantimetodetect]
            D2[GET /getmeantimetoacknowledge]
            D3[GET /geographicalalerts]
            D4[GET /incidentsbycategory]
        end
        
        subgraph "Analytics APIs"
            A1[GET /cyberkillchain]
            A2[GET /analystworkload]
            A3[GET /incidenttrends]
            A4[GET /threatactors]
        end
        
        subgraph "Configuration APIs"
            CF1[GET /categories]
            CF2[POST /categories]
            CF3[GET /severities]
            CF4[GET /sla]
        end
    end
```

### 6.2 Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant Client
    participant Middleware
    participant AuthService
    participant TenantDB
    participant CoreDB
    
    Client->>Middleware: Request with Access Token
    Middleware->>Middleware: Extract Tenant from URL/Header
    Middleware->>AuthService: Validate Token
    AuthService->>CoreDB: Check Token Validity
    CoreDB-->>AuthService: Token Info + User Details
    AuthService->>TenantDB: Get Tenant-specific Permissions
    TenantDB-->>AuthService: User Permissions
    AuthService-->>Middleware: Authorization Result
    Middleware->>Middleware: Route to Controller
    Note over Middleware: If auth fails, return 401/403
```

---

## 7. Technology Stack

### 7.1 Core Technologies
- **Programming Language**: Go (Golang) 1.17+
- **Web Framework**: Gorilla Mux (HTTP routing)
- **Database**: MongoDB (Primary), InfluxDB (Metrics)
- **Caching**: Redis
- **Containerization**: Docker
- **Build System**: Makefile

### 7.2 External Dependencies
- **SIEM Integrations**: QRadar, Azure Sentinel, Securonix, BluSapphire
- **Ticketing Systems**: ServiceNow integration
- **File Processing**: Excel/CSV export capabilities
- **Monitoring**: InfluxDB for system metrics
- **Security**: JWT token-based authentication

### 7.3 Libraries & Frameworks
```go
// Key Go modules
go.mongodb.org/mongo-driver    // MongoDB driver
github.com/gorilla/mux         // HTTP router
github.com/influxdata/influxdb-client-go/v2  // InfluxDB client
github.com/Luxurioust/excelize  // Excel processing
```

---

## 8. Security & Compliance

### 8.1 Security Features
- **Multi-factor Authentication**: Token-based auth with session management
- **Role-based Access Control**: Granular permissions per tenant
- **Data Encryption**: At-rest and in-transit encryption
- **Audit Logging**: Complete audit trail for all operations
- **Input Validation**: Comprehensive input sanitization
- **Session Management**: Secure session handling with timeouts

### 8.2 Compliance Standards
- **SOC 2**: Security controls and monitoring
- **ISO 27001**: Information security management
- **GDPR**: Data privacy and protection
- **NIST Cybersecurity Framework**: Security standards alignment

---

## 9. Performance & Scalability

### 9.1 Performance Characteristics
- **Horizontal Scaling**: Multi-tenant architecture supports scaling
- **Database Optimization**: Indexed queries and aggregation pipelines
- **Caching Strategy**: Redis caching for frequently accessed data
- **Connection Pooling**: Efficient database connection management
- **Background Processing**: Asynchronous task processing

### 9.2 Monitoring & Metrics
- **System Metrics**: CPU, Memory, Disk usage via InfluxDB
- **Application Metrics**: API response times, error rates
- **Business Metrics**: Incident volumes, case resolution times
- **Health Checks**: Service availability monitoring

---

## 10. Deployment Architecture

### 10.1 Multi-Tenant Deployment Model

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Load Balancer"
            LB[Application Load Balancer]
        end
        
        subgraph "Securaa SIEM Cluster"
            APP1[Securaa SIEM Instance 1]
            APP2[Securaa SIEM Instance 2]
            APP3[Securaa SIEM Instance N]
        end
        
        subgraph "Database Cluster"
            subgraph "Tenant Databases"
                DB1[(Tenant A DB)]
                DB2[(Tenant B DB)]
                DB3[(Tenant N DB)]
            end
            
            subgraph "Shared Infrastructure"
                CORE_DB[(Core DB)]
                INFLUX_DB[(InfluxDB)]
                REDIS_CACHE[(Redis Cache)]
            end
        end
        
        subgraph "External Integrations"
            SIEM_TOOLS[SIEM Tools]
            TICKETING[Ticketing Systems]
            THREAT_INTEL[Threat Intelligence]
        end
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB1
    APP1 --> DB2
    APP1 --> DB3
    APP1 --> CORE_DB
    APP1 --> INFLUX_DB
    APP1 --> REDIS_CACHE
    
    APP1 --> SIEM_TOOLS
    APP1 --> TICKETING
    APP1 --> THREAT_INTEL
```

### 10.2 Configuration Management
- **Environment-specific Configs**: Development, staging, production
- **Tenant-specific Settings**: Per-tenant customization
- **Feature Flags**: Dynamic feature enablement
- **Secret Management**: Secure credential storage

---

## 11. Business Logic Flow

### 11.1 Incident Processing Workflow

```mermaid
flowchart TD
    START([Incident Created]) --> VALIDATE{Validate Input}
    VALIDATE -->|Valid| ENRICH[Enrich with Metadata]
    VALIDATE -->|Invalid| REJECT[Reject & Log Error]
    
    ENRICH --> CATEGORIZE[Auto-categorize Incident]
    CATEGORIZE --> SEVERITY[Assign Severity Level]
    SEVERITY --> ASSIGN{Auto-assignment Rules?}
    
    ASSIGN -->|Yes| AUTO_ASSIGN[Assign to Analyst]
    ASSIGN -->|No| QUEUE[Add to Queue]
    
    AUTO_ASSIGN --> NOTIFY[Send Notifications]
    QUEUE --> NOTIFY
    
    NOTIFY --> CASE_GROUP{Group into Case?}
    CASE_GROUP -->|Yes| CREATE_CASE[Create/Update Case]
    CASE_GROUP -->|No| STORE[Store Individual Incident]
    
    CREATE_CASE --> PLAYBOOK{Trigger Playbook?}
    STORE --> PLAYBOOK
    
    PLAYBOOK -->|Yes| EXECUTE_PB[Execute Playbook]
    PLAYBOOK -->|No| MONITOR[Monitor & Track]
    
    EXECUTE_PB --> MONITOR
    MONITOR --> END([Incident in System])
    REJECT --> END
```

### 11.2 Case Management Workflow

```mermaid
stateDiagram-v2
    [*] --> New
    New --> Assigned : Analyst Assignment
    New --> InProgress : Start Investigation
    
    Assigned --> InProgress : Begin Work
    Assigned --> Escalated : Escalate Issue
    
    InProgress --> OnHold : Waiting for Info
    InProgress --> Resolved : Investigation Complete
    InProgress --> Escalated : Need Expertise
    
    OnHold --> InProgress : Info Received
    OnHold --> Closed : Timeout/Cancel
    
    Escalated --> InProgress : Expert Assigned
    Escalated --> Closed : Cannot Resolve
    
    Resolved --> Closed : Confirm Resolution
    Resolved --> InProgress : Reopen
    
    Closed --> [*]
    Closed --> InProgress : Reopen Case
```

---

## 12. Integration Points

### 12.1 SIEM Tool Integrations

| SIEM Tool | Integration Type | Data Flow | Authentication |
|-----------|------------------|-----------|----------------|
| QRadar | REST API | Bi-directional | API Key/OAuth |
| Azure Sentinel | REST API | Pull/Push | Service Principal |
| Securonix | REST API | Pull | API Token |
| BluSapphire | REST API | Pull | API Key |
| ElasticSearch | REST API | Pull/Push | Basic Auth |

### 12.2 External System APIs

```mermaid
graph LR
    subgraph "Securaa SIEM"
        CORE[Core Service]
    end
    
    subgraph "SIEM Tools"
        QRADAR[QRadar API]
        SENTINEL[Azure Sentinel API]
        SECURONIX[Securonix API]
    end
    
    subgraph "Ticketing"
        SN[ServiceNow API]
        JIRA[Jira API]
    end
    
    subgraph "Threat Intel"
        TI1[Threat Feed API]
        TI2[MITRE ATT&CK]
    end
    
    CORE <--> QRADAR
    CORE <--> SENTINEL
    CORE <--> SECURONIX
    CORE <--> SN
    CORE <--> JIRA
    CORE --> TI1
    CORE --> TI2
```

---

## 13. Error Handling & Resilience

### 13.1 Error Handling Strategy
- **Graceful Degradation**: Service continues with reduced functionality
- **Circuit Breaker Pattern**: Prevent cascade failures
- **Retry Mechanisms**: Configurable retry policies
- **Dead Letter Queues**: Handle failed message processing
- **Comprehensive Logging**: Structured logging for debugging

### 13.2 Disaster Recovery
- **Database Backups**: Regular automated backups
- **Multi-region Deployment**: Geographic redundancy
- **Health Monitoring**: Proactive health checks
- **Failover Procedures**: Automated failover capabilities

---

## 14. Future Roadmap

### 14.1 Planned Enhancements
- **Machine Learning Integration**: AI-powered threat detection
- **Advanced Analytics**: Predictive analytics capabilities
- **API Gateway**: Centralized API management
- **Microservices Migration**: Break down into smaller services

### 14.2 Technology Upgrades
- **Go Version**: Upgrade to latest Go versions
- **Database Optimization**: Performance improvements
- **Cloud Native**: Cloud-first architecture
- **Real-time Processing**: Stream processing capabilities

---

## 15. Conclusion

The Securaa SIEM service represents a comprehensive, enterprise-grade security information and event management platform. Its multi-tenant architecture, extensive integration capabilities, and robust feature set make it suitable for organizations of all sizes looking to enhance their security operations.

The modular design allows for easy maintenance and extension, while the Go-based implementation ensures high performance and scalability. The extensive API surface area provides flexibility for integration with existing security tools and workflows.

This high-level design serves as a blueprint for understanding the system architecture, data flows, and key components that make up the Securaa SIEM service.
