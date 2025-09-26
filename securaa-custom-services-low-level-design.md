# Low-Level Design (Low Level Design) - Securaa Custom Services

## 1. Implementation Overview

### 1.1 Technology Stack
- **Language**: Go 1.17
- **Web Framework**: Gorilla Mux
- **Database**: MongoDB with official Go driver
- **Cache**: Redis
- **Authentication**: JWT tokens with SAML integration
- **Encryption**: AES encryption for sensitive data
- **Containerization**: Docker
- **Build System**: Make with custom Makefile

### 1.2 Project Structure Analysis

```
zona_custom/
├── main.go                 # Application entry point
├── app.go                  # Application initialization and routing
├── go.mod                  # Go module dependencies
├── Dockerfile             # Container configuration
├── Makefile              # Build automation
├── constants/
│   └── constants.go       # Application constants
├── controllers/           # HTTP request handlers
│   ├── customAppController.go
│   ├── genericAppController.go
│   ├── exportController.go
│   ├── integrationController.go
│   └── eventsController.go
├── handlers/              # Error handling
│   └── errorHandler.go
├── models/                # Data structures
│   ├── Response.go
│   ├── export.go
│   ├── process.go
│   └── customtaskhandler.go
└── services/              # Business logic
    ├── exportservice.go
    ├── importservice.go
    ├── integrationservice.go
    └── eventsService.go
```

## 2. Detailed Component Design

### 2.1 Application Bootstrap (`main.go` & `app.go`)

#### 2.1.1 Main Function Flow

```go
func main() {
    securaalog.Init("CORE_SERVICE_LOGS")  // Initialize logging
    app := App{}                          // Create app instance
    app.Initialize()                      // Setup dependencies
    app.Run(":8063")                     // Start HTTP server
}
```

#### 2.1.2 App Structure Design

```go
type App struct {
    Router             *mux.Router                    // HTTP router
    AccessTokenHashMap map[string]int64               // Token cache
    DBSession          map[string]common.SessionStruct // DB connections
    ConfigObject       config.ConfigStruct           // Configuration
    BuildType          string                        // Deployment type
    RequestResponseLog bool                          // Logging flag
}
```

#### 2.1.3 Initialization Sequence

```mermaid
sequenceDiagram
    participant Main
    participant App
    participant Config
    participant MongoDB
    participant Router
    participant Cache
    
    Main->>App: Initialize()
    App->>Config: InitConfig()
    Config-->>App: Configuration loaded
    App->>MongoDB: InitMongoClient()
    MongoDB-->>App: Database connections established
    App->>Router: initializeRoutes()
    Router-->>App: Routes configured
    App->>Cache: CacheHealthCheck()
    Cache-->>App: Cache initialized
    App-->>Main: Initialization complete
    Main->>App: Run(":8063")
    App->>Router: http.ListenAndServe()
```

### 2.2 Database Connection Management

#### 2.2.1 Multi-Tenant Connection Strategy

```go
func (a *App) InitMongoClient(configObject config.ConfigStruct) {
    a.DBSession = make(map[string]common.SessionStruct)
    
    // Initialize core database connection
    mongoDbClient, err := mongo_driver.NewMongoClientWrapper(configObject, nil)
    clientStruct := common.SessionStruct{
        DBName: config["mongoDB"],
        Client: mongoDbClient,
    }
    a.DBSession["localhost"] = clientStruct
    
    // Initialize tenant-specific connections
    tenantsList, _ := utils.GetAllTenants2(mongoDbClient, configObject)
    for _, tenantData := range tenantsList {
        if a.BuildType == "mssp" && tenantData.Status == "active" {
            // MSSP: Each tenant has separate database
            tenantDBClient, _ := mongo_driver.NewMongoClientWrapper(configObject, tenantData)
            clientStruct := common.SessionStruct{
                DBName: tenantDBClient.DBName,
                Client: tenantDBClient,
            }
            a.DBSession[tenantCode] = clientStruct
        } else {
            // Single tenant: Shared database with tenant isolation
            // Implementation for single-tenant architecture
        }
    }
}
```

#### 2.2.2 Connection Pool Management

```mermaid
graph TB
    subgraph "Connection Pool Strategy"
        MAIN_POOL[Main Connection Pool<br/>localhost]
        TENANT1_POOL[Tenant 1 Pool<br/>tenant-1-db]
        TENANT2_POOL[Tenant 2 Pool<br/>tenant-2-db]
        TENANT_N_POOL[Tenant N Pool<br/>tenant-n-db]
    end
    
    subgraph "Pool Configuration"
        MIN_CONN[Min Connections: 5]
        MAX_CONN[Max Connections: 100]
        IDLE_TIMEOUT[Idle Timeout: 10m]
        CONN_TIMEOUT[Connection Timeout: 30s]
    end
    
    MAIN_POOL --> MIN_CONN
    TENANT1_POOL --> MAX_CONN
    TENANT2_POOL --> IDLE_TIMEOUT
    TENANT_N_POOL --> CONN_TIMEOUT
```

### 2.3 Middleware Implementation

#### 2.3.1 Logging Middleware

```go
func (a *App) loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        middleWareData := common.MiddleWareData{
            LogRequestResponse:   a.RequestResponseLog,
            DBSession:          a.DBSession,
            ConfigObject:       a.ConfigObject,
            AccessTokenHashMap: a.AccessTokenHashMap,
        }
        
        err := common.MiddleWareForMongoDriver(next, w, r, 
            constants.SkipRoutes, constants.SkipURI, middleWareData)
        
        if err != nil {
            logger.Error("Error in Middleware : ", err.Error())
            utils.RespondWithJSON(w, http.StatusOK, 
                common.HandleError(err, "Error in creating Tenant Session"))
            return
        }
    })
}
```

#### 2.3.2 Middleware Processing Flow

```mermaid
flowchart TD
    A[HTTP Request] --> B[Logging Middleware]
    B --> C{Skip Routes Check}
    C -->|Skip| D[Direct Route]
    C -->|Process| E[Token Validation]
    E --> F{Valid Token?}
    F -->|No| G[Return 401]
    F -->|Yes| H[Tenant Resolution]
    H --> I{Tenant Valid?}
    I -->|No| J[Return 403]
    I -->|Yes| K[Session Creation]
    K --> L[Request Logging]
    L --> M[Forward to Controller]
    M --> N[Response Logging]
    N --> O[HTTP Response]
    
    G --> O
    J --> O
    D --> O
```

### 2.4 Controller Layer Implementation

#### 2.4.1 Custom App Controller

```go
type CustomAppController struct{}

func (gc CustomAppController) DeleteApp(w http.ResponseWriter, r *http.Request, 
    dbSession map[string]common.SessionStruct, configObject config.ConfigStruct) {
    
    response := models.Response{}
    deleteAppRequest := models.DeleteApp{}
    
    // Step 1: Decode request
    decoder := json.NewDecoder(r.Body)
    if err := decoder.Decode(&deleteAppRequest); err != nil {
        utils.RespondWithJSON(w, http.StatusOK, 
            handlers.HandleError(err, "Error in Reading Request"))
        return
    }
    defer r.Body.Close()
    
    // Step 2: Get database client
    mongoDBClient := dbSession[deleteAppRequest.TenantCode].Client
    
    // Step 3: Business logic execution
    err := deleteAppRequest.UpdateTasksStatus(mongoDBClient, configObject)
    if err != nil {
        utils.RespondWithJSON(w, http.StatusOK, 
            handlers.HandleError(err, "Error in updating task status"))
        return
    }
    
    // Step 4: Update database
    colQuerier := bson.M{"integration_id": deleteAppRequest.IntegrationID}
    change := bson.M{"$set": bson.M{"status": "deleted"}}
    mongoDBClient.CollectionName = config["mongoIntegartionCollection"]
    err = mongoDBClient.UpdateSingleDocument(colQuerier, change, nil, false)
    
    // Step 5: Cache invalidation
    RemoveAppListingCache(deleteAppRequest.TenantCode)
    RemoveActiveInstanceCache(deleteAppRequest.TenantCode)
    
    // Step 6: Response
    response.Success = true
    response.DisplayMessage = "App Deleted"
    utils.RespondWithJSON(w, http.StatusOK, response)
}
```

#### 2.4.2 Generic App Controller - UpsertGenericApp

```mermaid
flowchart TD
    A[UpsertGenericApp Request] --> B[Parse Multipart Form]
    B --> C{Logo File Present?}
    C -->|Yes| D[Process Logo Upload]
    C -->|No| E[Use Default Logo]
    D --> F[Parse Form Fields]
    E --> F
    F --> G[Decrypt Credentials]
    G --> H{Integration ID = 0?}
    H -->|Yes| I[Create New Integration]
    H -->|No| J[Update Existing Integration]
    
    I --> K[Check Name Availability]
    K --> L{Name Available?}
    L -->|No| M[Return Error]
    L -->|Yes| N[Generate Integration ID]
    N --> O[Insert Database]
    
    J --> P[Update Active Instances]
    P --> Q[Update Integration Data]
    Q --> R{Logo Updated?}
    R -->|Yes| S[Update Task Logos]
    R -->|No| T[Skip Logo Update]
    S --> T
    
    O --> U{Add Instance?}
    T --> U
    U -->|No| V[Cache Invalidation]
    U -->|Yes| W[Check Trial Limits]
    W --> X{Limit Exceeded?}
    X -->|Yes| Y[Return Limit Error]
    X -->|No| Z[Create Active Instance]
    Z --> AA[Update Trial Count]
    AA --> V
    V --> BB[Return Success]
    
    M --> BB
    Y --> BB
```

### 2.5 Service Layer Implementation

#### 2.5.1 Export Service Architecture

```go
func ExportIntegration(dbSession map[string]common.SessionStruct, 
    config config.Config, req models.ExportAppInputStruct) models.Response {
    
    var response models.Response
    var integrations models.ExportObject
    var apps []models.AppData
    
    tenantCode := req.Tenantcode
    mongoDBClient := dbSession[tenantCode].Client
    
    for _, eachIntegrationID := range req.IntegrationIds {
        var integrationObj models.AppData
        
        // Step 1: Fetch integration data
        var appObj models.GenericIntegrationObject
        mongoDBClient.CollectionName = config["mongoIntegartionCollection"]
        err := mongoDBClient.FindSingleDocument(
            bson.M{"integration_id": eachIntegrationID, "status": "active"}, 
            nil, &appObj)
        
        // Step 2: Sanitize sensitive data
        var updatedFields []models.Field
        for _, eachfield := range appObj.Fields {
            eachfield.Value = "" // Remove sensitive values
            updatedFields = append(updatedFields, eachfield)
        }
        
        // Step 3: Fetch related tasks
        var tasksResponse []models.TaskData
        mongoDBClient.CollectionName = config["taskCollection"]
        err = mongoDBClient.FindMultipleDocuments(
            bson.M{"integration_id": integrationID, "status": bson.M{"$in": status}}, 
            nil, &tasksResponse)
        
        // Step 4: Process tasks and dependencies
        altTasksResponse := processTasks(tasksResponse)
        
        integrationObj.App = appObj
        integrationObj.Tasks = altTasksResponse
        apps = append(apps, integrationObj)
    }
    
    integrations.Apps = apps
    response.Success = true
    response.Data = integrations
    return response
}
```

#### 2.5.2 Task Dependency Mapping

```mermaid
graph TB
    subgraph "Task Processing Pipeline"
        A[Fetch Tasks] --> B[Build Task Name Map]
        B --> C[Process Non-Ingestion Tasks]
        B --> D[Process Case Ingestion Tasks]
        
        C --> E[Sanitize Task Data]
        D --> F[Map Dependent Tasks]
        D --> G[Map Events API Tasks]
        
        E --> H[Replace Task IDs with Names]
        F --> H
        G --> H
        
        H --> I[Generate Export Object]
    end
    
    subgraph "Dependency Resolution"
        J[Task ID] --> K[Task Name Lookup]
        K --> L[Replace in Config JSON]
        L --> M[Update Dependencies]
    end
    
    subgraph "Data Sanitization"
        N[Remove Sensitive Data]
        O[Reset IDs to 0]
        P[Clear Tenant Info]
        Q[Clear Task Handlers]
    end
    
    E --> N
    E --> O
    E --> P
    E --> Q
```

### 2.6 Data Models Implementation

#### 2.6.1 Core Data Structures

```go
// Response model - Standard API response
type Response struct {
    Success        bool        `json:"success"`
    Data           interface{} `json:"data,omitempty"`
    Error          string      `json:"error,omitempty"`
    Time           int64       `json:"time,omitempty"`
    DisplayMessage string      `json:"displaymessage,omitempty"`
    Status         string      `json:"status,omitempty"`
    ErrorPath      string      `json:"errorpath,omitempty"`
    SessionExpired bool        `json:"sessionexpired,omitempty"`
    FileName       string      `json:"filename,omitempty"`
    Field          []string    `json:"field,omitempty"`
    Count          int         `json:"count,omitempty"`
}

// GenericIntegrationObject - Integration data structure
type GenericIntegrationObject struct {
    IntegrationID int           `json:"integration_id" bson:"integration_id"`
    Title         string        `json:"title" bson:"title"`
    Description   string        `json:"description" bson:"description"`
    Version       string        `json:"version" bson:"version"`
    Category      string        `json:"category" bson:"category"`
    TenantCode    string        `json:"tenant_code" bson:"tenant_code"`
    Fields        []Field       `json:"fields" bson:"fields"`
    Status        string        `json:"status" bson:"status"`
    Logo          string        `json:"logo" bson:"logo"`
    GenericApp    bool          `json:"generic_app" bson:"generic_app"`
    UserID        int           `json:"user_id" bson:"user_id"`
    AddInstance   bool          `json:"add_instance" bson:"add_instance"`
}

// TaskData - Task information structure
type TaskData struct {
    ID                  int    `json:"id" bson:"id"`
    Name                string `json:"name" bson:"name"`
    TasksTag            string `json:"tasks_tag" bson:"tasks_tag"`
    TaskHandler         string `json:"task_handler" bson:"task_handler"`
    IntegrationID       int    `json:"integration_id" bson:"integration_id"`
    Fields              string `json:"fields" bson:"fields"`
    Status              string `json:"status" bson:"status"`
    Tenantcode          string `json:"tenantcode" bson:"tenantcode"`
    IngestCases         bool   `json:"ingest_cases" bson:"ingest_cases"`
    CaseIngestionConfig string `json:"case_ingestion_config" bson:"case_ingestion_config"`
    EventsAPIConfig     string `json:"events_api_config" bson:"events_api_config"`
    LogoPath            string `json:"logo_path" bson:"logo_path"`
}
```

#### 2.6.2 Data Validation & Transformation

```mermaid
flowchart LR
    subgraph "Input Validation"
        A[Raw Input] --> B[JSON Decode]
        B --> C[Structure Validation]
        C --> D[Business Rules Check]
        D --> E[Sanitization]
    end
    
    subgraph "Data Transformation"
        F[Database Model] --> G[Field Encryption]
        G --> H[Tenant Mapping]
        H --> I[Timestamp Addition]
        I --> J[ID Generation]
    end
    
    subgraph "Output Serialization"
        K[Internal Model] --> L[Response Model]
        L --> M[JSON Encode]
        M --> N[HTTP Response]
    end
    
    E --> F
    J --> K
```

### 2.7 Error Handling Strategy

#### 2.7.1 Error Handler Implementation

```go
func HandleError(err error, message string) models.Response {
    response := models.Response{
        Success:        false,
        Error:          err.Error(),
        DisplayMessage: message,
        Time:           time.Now().UnixNano() / 1000000,
    }
    
    // Log error details
    logger.Error("Error: %s, Message: %s", err.Error(), message)
    
    return response
}
```

#### 2.7.2 Error Flow Hierarchy

```mermaid
graph TB
    A[Request Processing] --> B{Validation Error?}
    B -->|Yes| C[Return 400 Bad Request]
    B -->|No| D[Business Logic]
    
    D --> E{Database Error?}
    E -->|Yes| F[Log Error]
    F --> G[Return 500 Internal Server Error]
    E -->|No| H[Processing Success]
    
    D --> I{Business Logic Error?}
    I -->|Yes| J[Log Warning]
    J --> K[Return 200 with Error Flag]
    I -->|No| H
    
    H --> L[Return 200 Success]
    
    subgraph "Error Types"
        M[Validation Errors]
        N[Database Errors]
        O[Business Logic Errors]
        P[System Errors]
    end
    
    C --> M
    G --> N
    K --> O
    G --> P
```

### 2.8 Authentication & Authorization

#### 2.8.1 Token Management

```go
type App struct {
    AccessTokenHashMap map[string]int64  // Token -> Expiry mapping
    // ... other fields
}

func (a *App) UpdateUserSessionExpiryTime(accessToken string, expiryTime int64) {
    a.AccessTokenHashMap[accessToken] = expiryTime
}

func (a *App) ValidateToken(token string) bool {
    expiryTime, exists := a.AccessTokenHashMap[token]
    if !exists {
        return false
    }
    
    currentTime := time.Now().UnixNano() / 1000000
    return currentTime < expiryTime
}
```

#### 2.8.2 Security Flow

```mermaid
sequenceDiagram
    participant Client
    participant Middleware
    participant TokenStore
    participant Database
    participant Controller
    
    Client->>Middleware: Request with Token
    Middleware->>TokenStore: Validate Token
    TokenStore-->>Middleware: Token Valid/Invalid
    
    alt Token Invalid
        Middleware-->>Client: 401 Unauthorized
    else Token Valid
        Middleware->>Database: Get Tenant Info
        Database-->>Middleware: Tenant Details
        Middleware->>Controller: Forward Request
        Controller-->>Middleware: Process Response
        Middleware-->>Client: Success Response
    end
```

### 2.9 Caching Strategy

#### 2.9.1 Cache Implementation

```go
func RemoveAppListingCache(tenantCode string) {
    cacheKey := fmt.Sprintf("app_listing_%s", tenantCode)
    cache.Delete(cacheKey)
}

func RemoveActiveInstanceCache(tenantCode string) {
    cacheKey := fmt.Sprintf("active_instances_%s", tenantCode)
    cache.Delete(cacheKey)
}

func GetAppListingFromCache(tenantCode string) ([]models.AppData, bool) {
    cacheKey := fmt.Sprintf("app_listing_%s", tenantCode)
    data, exists := cache.Get(cacheKey)
    if exists {
        var apps []models.AppData
        json.Unmarshal(data, &apps)
        return apps, true
    }
    return nil, false
}
```

#### 2.9.2 Cache Invalidation Strategy

```mermaid
graph TB
    subgraph "Cache Operations"
        A[Create/Update Operation] --> B[Invalidate Related Cache]
        C[Delete Operation] --> D[Invalidate Related Cache]
        E[Read Operation] --> F{Cache Hit?}
        F -->|Yes| G[Return Cached Data]
        F -->|No| H[Fetch from DB]
        H --> I[Store in Cache]
        I --> J[Return Data]
    end
    
    subgraph "Cache Keys"
        K[app_listing_{tenant}]
        L[active_instances_{tenant}]
        M[integration_list_{tenant}]
    end
    
    B --> K
    B --> L
    D --> K
    D --> L
```

### 2.10 Configuration Management

#### 2.10.1 Configuration Structure

```go
type ConfigStruct struct {
    ConfigFilePath string
    ConfigData     map[string]string
}

func InitConfig() ConfigStruct {
    config := ConfigStruct{
        ConfigFilePath: "/opt/securaa/conf/securaa.conf",
        ConfigData:     make(map[string]string),
    }
    
    // Load configuration from file
    configData, err := config.ReadConfig()
    if err != nil {
        logger.Error("Failed to load configuration: %v", err)
    }
    
    config.ConfigData = configData
    return config
}
```

#### 2.10.2 Configuration Flow

```mermaid
flowchart TD
    A[Application Start] --> B[Load Config File]
    B --> C[Parse Configuration]
    C --> D[Validate Required Keys]
    D --> E{Validation OK?}
    E -->|No| F[Exit with Error]
    E -->|Yes| G[Store in ConfigObject]
    G --> H[Pass to Components]
    
    subgraph "Config Categories"
        I[Database Settings]
        J[Cache Settings]
        K[Security Settings]
        L[Logging Settings]
        M[Business Logic Settings]
    end
    
    H --> I
    H --> J
    H --> K
    H --> L
    H --> M
```

### 2.11 Database Operations

#### 2.11.1 CRUD Operations Pattern

```go
// Generic database operation wrapper
type DatabaseOperations struct {
    Client         mongo_driver.MongoClientWrapper
    CollectionName string
}

func (db *DatabaseOperations) Create(document interface{}) error {
    db.Client.CollectionName = db.CollectionName
    return db.Client.InsertSingleDocument(document, nil)
}

func (db *DatabaseOperations) Read(filter bson.M, result interface{}) error {
    db.Client.CollectionName = db.CollectionName
    return db.Client.FindSingleDocument(filter, nil, result)
}

func (db *DatabaseOperations) Update(filter bson.M, update bson.M) error {
    db.Client.CollectionName = db.CollectionName
    return db.Client.UpdateSingleDocument(filter, update, nil, false)
}

func (db *DatabaseOperations) Delete(filter bson.M) error {
    db.Client.CollectionName = db.CollectionName
    return db.Client.DeleteSingleDocument(filter, nil)
}
```

#### 2.11.2 Transaction Management

```mermaid
sequenceDiagram
    participant Service
    participant DBClient
    participant MongoDB
    
    Service->>DBClient: Start Transaction
    DBClient->>MongoDB: Begin Transaction
    
    loop Database Operations
        Service->>DBClient: Execute Operation
        DBClient->>MongoDB: Execute Query
        MongoDB-->>DBClient: Operation Result
        DBClient-->>Service: Result
    end
    
    alt All Operations Successful
        Service->>DBClient: Commit Transaction
        DBClient->>MongoDB: Commit
        MongoDB-->>DBClient: Success
        DBClient-->>Service: Transaction Complete
    else Any Operation Failed
        Service->>DBClient: Rollback Transaction
        DBClient->>MongoDB: Rollback
        MongoDB-->>DBClient: Rollback Complete
        DBClient-->>Service: Transaction Rolled Back
    end
```

### 2.12 Logging Implementation

#### 2.12.1 Structured Logging

```go
var logger = securaalog.New("zona_custom")

func LogRequest(r *http.Request) {
    logger.Info("Request received",
        "method", r.Method,
        "url", r.URL.String(),
        "remote_addr", r.RemoteAddr,
        "user_agent", r.UserAgent(),
    )
}

func LogError(operation string, err error, context map[string]interface{}) {
    logger.Error("Operation failed",
        "operation", operation,
        "error", err.Error(),
        "context", context,
    )
}

func LogPerformance(operation string, duration time.Duration) {
    logger.Info("Operation completed",
        "operation", operation,
        "duration_ms", duration.Milliseconds(),
    )
}
```

#### 2.12.2 Log Levels & Categories

```mermaid
graph TB
    subgraph "Log Levels"
        A[DEBUG - Development Info]
        B[INFO - General Information]
        C[WARN - Warning Conditions]
        D[ERROR - Error Conditions]
        E[FATAL - Critical Errors]
    end
    
    subgraph "Log Categories"
        F[REQUEST_RESPONSE - HTTP Traffic]
        G[DATABASE - DB Operations]
        H[BUSINESS_LOGIC - Application Logic]
        I[SECURITY - Auth/Authorization]
        J[PERFORMANCE - Performance Metrics]
    end
    
    subgraph "Log Destinations"
        K[Console Output]
        L[File System]
        M[Centralized Logging]
        N[Monitoring Systems]
    end
    
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    
    F --> K
    G --> L
    H --> M
    I --> N
```

## 3. Performance Considerations

### 3.1 Optimization Strategies

#### 3.1.1 Database Query Optimization
- Use appropriate indexes on frequently queried fields
- Implement query result caching for read-heavy operations
- Use batch operations for bulk data manipulation
- Implement connection pooling for database efficiency

#### 3.1.2 Memory Management
- Implement proper cleanup of temporary objects
- Use connection pooling to avoid resource leaks
- Monitor goroutine lifecycle for concurrent operations
- Implement request timeout mechanisms

#### 3.1.3 Network Optimization
- Compress HTTP responses for large payloads
- Implement request/response caching
- Use HTTP/2 where supported
- Minimize JSON payload sizes

### 3.2 Scalability Considerations

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        A[Load Balancer] --> B[Instance 1]
        A --> C[Instance 2]
        A --> D[Instance N]
    end
    
    subgraph "Vertical Scaling"
        E[CPU Scaling]
        F[Memory Scaling]
        G[Storage Scaling]
    end
    
    subgraph "Database Scaling"
        H[Read Replicas]
        I[Sharding]
        J[Connection Pooling]
    end
    
    B --> H
    C --> I
    D --> J
```

## 4. Testing Strategy

### 4.1 Unit Testing Structure

```go
func TestDeleteApp(t *testing.T) {
    // Arrange
    controller := NewCustomAppController()
    mockDBSession := createMockDBSession()
    mockConfig := createMockConfig()
    
    // Act
    response := controller.DeleteApp(nil, createMockRequest(), mockDBSession, mockConfig)
    
    // Assert
    assert.True(t, response.Success)
    assert.Equal(t, "App Deleted", response.DisplayMessage)
}
```

### 4.2 Integration Testing

```mermaid
flowchart TD
    A[Integration Test Suite] --> B[Database Tests]
    A --> C[API Endpoint Tests]
    A --> D[Cache Integration Tests]
    A --> E[External Service Tests]
    
    B --> F[CRUD Operations]
    B --> G[Transaction Tests]
    
    C --> H[Authentication Tests]
    C --> I[Authorization Tests]
    C --> J[Input Validation Tests]
    
    D --> K[Cache Hit/Miss Tests]
    D --> L[Cache Invalidation Tests]
    
    E --> M[MongoDB Integration]
    E --> N[Redis Integration]
    E --> O[External API Integration]
```

## 5. Security Implementation

### 5.1 Data Encryption

```go
func EncryptSensitiveFields(fields map[string]string, config config.ConfigStruct) (map[string]string, error) {
    encryptedFields := make(map[string]string)
    encryptionKey := config["zonaCredentialsEncryptDecryptKey"]
    
    for key, value := range fields {
        if isSensitiveField(key) {
            encryptedValue, err := utils.CredentialsEncrypt(value, encryptionKey)
            if err != nil {
                return nil, err
            }
            encryptedFields[key] = encryptedValue
        } else {
            encryptedFields[key] = value
        }
    }
    
    return encryptedFields, nil
}

func isSensitiveField(fieldName string) bool {
    sensitiveFields := []string{"password", "api_key", "secret", "token"}
    for _, sensitive := range sensitiveFields {
        if strings.Contains(strings.ToLower(fieldName), sensitive) {
            return true
        }
    }
    return false
}
```

### 5.2 Input Sanitization

```mermaid
flowchart TD
    A[User Input] --> B[Input Validation]
    B --> C{Valid Format?}
    C -->|No| D[Return Validation Error]
    C -->|Yes| E[SQL Injection Check]
    E --> F{Safe?}
    F -->|No| G[Return Security Error]
    F -->|Yes| H[XSS Prevention]
    H --> I[Sanitized Input]
    I --> J[Business Logic Processing]
```

## 6. Deployment & Operations

### 6.1 Build Process

```makefile
# Build configuration from Makefile
build: builddir
	$(BUILD_ENV) go build -mod vendor $(BUILD_FLAGS) -o build/$(TARGET)

image_ecr: builddir
	DOCKER_BUILDKIT=1 docker build --pull \
	-t $(RUNTIME_DOCKER_IMAGE_ECR):latest \
	--build-arg TARGET=$(TARGET) \
	--build-arg GIT_REF=$(GIT_REF) \
	--build-arg BUILD_VERSION=$(BUILD_VERSION) .
```

### 6.2 Health Monitoring

```go
func HealthCheck() http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        health := struct {
            Status    string `json:"status"`
            Database  string `json:"database"`
            Cache     string `json:"cache"`
            Version   string `json:"version"`
            Timestamp int64  `json:"timestamp"`
        }{
            Status:    "healthy",
            Database:  checkDatabaseHealth(),
            Cache:     checkCacheHealth(),
            Version:   BuildVersion,
            Timestamp: time.Now().Unix(),
        }
        
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(health)
    }
}
```

This comprehensive Low-Level Design document provides detailed implementation specifications for the Securaa Custom Services application, covering all major components, data flows, and architectural decisions at the code level.