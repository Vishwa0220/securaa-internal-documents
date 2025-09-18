# Low-Level Design (LLD) – zona_process_manager

---

## 1. Detailed Component Design

### Class Diagrams (Mermaid)
```mermaid
classDiagram
    class main {
        +main()
        +RestartThroughPatch()
        +cleanup(cli, command)
        +deploySecuraa(command)
        +StartMetaDB(cli, tag, configObject, conf)
        +StartShardCluster(isPassive, cli, tag, config, configObject)
        +StartShardHandler(cli, conf, configObject)
        +InitSecuraaAppsContext()
        +SetSecuraaAppsContext(activeIntegrations, dbSession, configObject)
        +InitializeMongoDBReplicaSet(isActive, isSecondaryActive, config, configStruct)
        +checkMongoServiceReachability(serviceName, config, port)
        +passiveServerUp(conf)
        +completeSOARUp(conf, cli)
        +isActive(conf)
        +isPassive(conf)
        +isSecondaryActive(conf)
        +isServiceVM(conf)
        +isDBVM(conf)
        +checkAndUpdateActiveServerInfo(mongodbSession, mongoDbHost, conf)
        +checkAndUpdatePassiveServerInfo(mongoMetaDBClient, mongoDbHost, conf)
        +changeServerType(mongoDefaultClient, currentServerHost, serverType, state, conf)
        +updateMetaDbMembers(mongoMetaDBClient, currentServerHost, serverType, priority)
        +updateConfigServerMembers(mongoMetaDBClient, currentServerHost, serverType, priority, configObject)
        +updateShardMembers(mongoMetaDBClient, currentServerHost, serverType, priority, configObject)
        +changePriority(replicaSetDbClient, replicaSetName, currentServerHost, replicaSetPort, priority)
    }
    class common {
        +ServiceData
        +IsServer()
        +CheckIfCaseGroupingEnabled()
        +SystemServices
        +CoreServices
        +BatchServices
        +SecuraaAppServices
        +AccessTokenHashMap
        +DBSession
        +ConfigObject
        +ActiveIntegrations
        +BuildType
    }
    class docker {
        +InitDockerServiceContexts()
        +checkVolumeExists(volumeName)
        +createVolume(volumeName)
        +createNFSVolume(volumeName)
        +removeVolume(volumeName)
        +VerifyVolumeExistance(volumeName)
        +CreateServices(cli, dockerTag, PatchTag, patchServiceLists)
        +InitSystemServicesContext()
        +InitCoreServicesContext()
        +InitBatchesContext()
        +GetContainerIDByServiceName(cli, serviceName)
        +RunCommandInContainer(cli, containerId, commands)
        +SetupUtilsPackages(cli)
        +CreateUIServices(cli, dockerTag, PatchTag, patchServiceLists)
        +CreateServiceWithContext(cli, Ctx)
        +CreateZookeeperKafkaService(cli)
    }
    class models {
        +IntegrationsResponse
        +Response
        +Tenant
        +TenantDB
        +ClientInfo
        +SessionStruct
        +SystemData
        +TenantBackup
        +UserIntegrationPortObject
        +GetActiveIntegrations(dbSession, configObject, buildType)
        +getActiveIntegrations(dbSession, configObject, buildType)
        +GetPort(integrationID, executable, configObject, dbSession)
        +GetAppParams(paramType, configObject, dbSession, buildName)
    }
```

### Data Structures & Relationships
- `ServiceData`: Represents a service with name, context, port, replicas.
- `IntegrationsResponse`: Integration metadata for tenants.
- `Tenant`, `TenantDB`, `TenantBackup`: Tenant and database details.
- `SessionStruct`: MongoDB session wrapper.
- Global maps: `SystemServices`, `CoreServices`, `BatchServices`, `SecuraaAppServices` (all map[string]ServiceData).

---

## 2. Database Design

### Entity Relationship Diagram (Mermaid)
```mermaid
erDiagram
    TENANT ||--o{ TENANTDB : has
    TENANT ||--o{ TENANTBACKUP : backup
    TENANTDB ||--o{ INTEGRATIONSRESPONSE : integrates
    TENANTDB {
        int id
        string name
        string tenantcode
        string status
        string db_host
        string db_username
        string db_password
        string db_name
        string connection_status
        string uuid
    }
    INTEGRATIONSRESPONSE {
        int integration_id
        string title
        string action
        string serviceName
        string executionDir
        string status
        string executable
        string tenantcode
    }
    TENANT {
        int id
        string name
        string tenantcode
        string status
        string db_host
        string db_username
        string db_password
        string db_name
        string connection_status
    }
    TENANTBACKUP {
        int id
        string name
        string tenantcode
        string status
        string db_host
        string db_username
        string db_password
        string db_name
        string connection_status
        string uuid
    }
```

### Table Schemas
- **TENANT**: id (int), name (string), tenantcode (string), status (string), db_host (string), db_username (string), db_password (string), db_name (string), connection_status (string)
- **TENANTDB**: id (int), name (string), tenantcode (string), status (string), db_host (string), db_username (string), db_password (string), db_name (string), connection_status (string), uuid (string)
- **INTEGRATIONSRESPONSE**: integration_id (int), title (string), action (string), serviceName (string), executionDir (string), status (string), executable (string), tenantcode (string)
- **TENANTBACKUP**: id (int), name (string), tenantcode (string), status (string), db_host (string), db_username (string), db_password (string), db_name (string), connection_status (string), uuid (string)

### Relationships
- One tenant can have multiple databases and backups.
- Each database can have multiple integrations.

---

## 3. API Design Details

> The codebase does not expose HTTP endpoints directly; orchestration is via CLI and Docker APIs. If extended to REST, typical endpoints would be:

| Endpoint | Method | Request Schema | Response Schema | Auth |
|----------|--------|---------------|----------------|------|
| /service/start | POST | {serviceName: string} | {status: string, details: object} | Token |
| /service/stop | POST | {serviceName: string} | {status: string} | Token |
| /integration/list | GET | - | [IntegrationsResponse] | Token |
| /tenant/list | GET | - | [Tenant] | Token |
| /status | GET | - | {services: [...], integrations: [...]} | Token |

- **Authentication:** Token-based (JWT or API key recommended)
- **Request/Response Schemas:** Use JSON, matching Go struct fields

---

## 4. Sequence Diagrams (Mermaid)

### Service Startup Workflow
```mermaid
sequenceDiagram
    participant User
    participant Main
    participant Common
    participant Docker
    participant Models
    participant MongoDB
    User->>Main: start command
    Main->>Common: Load config
    Main->>Docker: Init service contexts
    Docker->>Docker: Create volumes/services
    Main->>Models: Fetch integrations
    Models->>MongoDB: Query tenant/integration data
    Models-->>Main: Integration data
    Main->>Docker: Deploy integration services
    Docker-->>Main: Status
    Main->>User: Success/Failure
```

### Inter-Service Communication
```mermaid
sequenceDiagram
    participant Main
    participant Docker
    participant Models
    participant MongoDB
    Main->>Docker: Create/Update service
    Docker->>Models: Request integration config
    Models->>MongoDB: Fetch integration details
    MongoDB-->>Models: Integration data
    Models-->>Docker: Config
    Docker-->>Main: Status
```

### Error Handling Scenario
```mermaid
sequenceDiagram
    participant Main
    participant Docker
    participant Models
    participant MongoDB
    Main->>Docker: Create service
    Docker-->>Main: Error (e.g., volume missing)
    Main->>Docker: Create volume
    Docker-->>Main: Success
    Main->>Docker: Retry service creation
    Docker-->>Main: Success/Failure
```

---

## 5. Implementation Details

### Design Patterns
- **Singleton:** Global config/state objects in `common/`
- **Factory:** Service context creation in `docker/`
- **Repository:** Data access patterns in `models/`
- **Observer:** Patch-based restart monitoring

### Algorithms & Data Structures
- Maps for service contexts and integration lists
- Iterative service deployment and health checks
- Dynamic port and parameter resolution for integrations

### Code Organization
- `/main.go`: Orchestration logic
- `/common/`: Global state, utilities
- `/docker/`: Docker orchestration
- `/models/`: Data models, integration logic

---

## 6. Technical Specifications

### Configuration Management
- Centralized config object loaded at startup
- Shared across modules via `common/`
- Supports dynamic updates and patch-based restarts

### Error Handling Strategies
- Centralized logging via `securaa_lib`
- Error propagation and handling in all major methods
- Retry logic for critical operations (e.g., MongoDB reachability)

### Performance Considerations
- Asynchronous service startup and monitoring
- Efficient use of maps for service/integration lookup
- Docker-based scaling and replica management

---

## Summary
This LLD provides a detailed breakdown of the zona_process_manager codebase, including class diagrams, database design, (potential) API details, sequence diagrams, implementation patterns, and technical specifications. All diagrams use actual class and method names from the codebase for clarity and traceability.
