# Nuwa 类图与架构设计文档

本文档提供 Nuwa 项目中各个模块和类的详细类图，便于架构优化和重构分析。

## 📋 目录结构概览

```text
src/
├── api/                    # API 接口层
│   ├── routers/           # API 路由控制器
│   ├── models/            # API 数据模型
│   ├── middleware/        # 中间件
│   └── dependencies.py    # 依赖注入
├── core/                  # 核心业务层
│   ├── orchestration/     # 编排引擎
│   ├── ai/               # AI 管理
│   ├── plugin/           # 插件系统
│   ├── tasks/            # 任务处理
│   ├── mcp/              # MCP 协议
│   ├── config/           # 配置管理
│   ├── di/               # 依赖注入
│   ├── scheduler/        # 任务调度
│   └── utils/            # 工具类
└── tests/                 # 测试代码
```

## 🎭 编排引擎 (Orchestration)

### IntelligentRouter 类图

```mermaid
classDiagram
    class IntelligentRouter {
        -plugin_manager: PluginManager
        -ai_manager: AIManager
        -TaskPlanner: TaskPlanner
        -model: Any
        +__init__(plugin_manager, ai_manager, TaskPlanner, model)
        +analyze_and_plan(user_input: str) PlanResult
        -list_available_plugins() List~PluginRegistration~
        -get_plugin_functions(selected_plugins) List~Dict~
        -log_plan_result(plan_result: PlanResult) void
    }
    
    class TaskPlanner {
        -prompt_templates: Any
        -ai_manager: AIManager
        -primary_provider: str
        -fallback_providers: List~str~
        -choose_model: str
        +__init__(prompt_templates, ai_manager)
        +select_plugins(user_input, plugins_basic_info) List~Dict~
        +plan_execution(user_input, plugin_functions) ExecutionPlan
    }
    
    class PlanResult {
        +success: bool
        +error: str
        +user_input: str
        +selected_plugins: List~str~
        +execution_plan: ExecutionPlan
        +suggestion: str
        +error_result(error, **kwargs)$ PlanResult
        +success_result(**kwargs)$ PlanResult
    }
    
    class ExecutionPlan {
        +steps: List~ExecutionStep~
        +from_content(content: str)$ ExecutionPlan
    }
    
    IntelligentRouter --> TaskPlanner: uses
    IntelligentRouter --> PlanResult: returns
    TaskPlanner --> ExecutionPlan: returns
    PlanResult --> ExecutionPlan: contains
```

### 编排引擎依赖关系

```mermaid
classDiagram
    class IntelligentRouter {
        +analyze_and_plan()
    }
    
    class TaskPlanner {
        +select_plugins()
        +plan_execution()
    }
    
    class AIManager {
        +call_with_fallback()
    }
    
    class PluginManager {
        +list_available_plugins()
        +get_plugin_functions()
    }
    
    IntelligentRouter --> TaskPlanner
    IntelligentRouter --> AIManager
    IntelligentRouter --> PluginManager
    TaskPlanner --> AIManager
```

## 🤖 AI 管理模块

### AIManager 类图

```mermaid
classDiagram
    class AIManager {
        -configs: List~AIModel~
        -_providers: Dict~str, BaseAIProvider~
        -primary_provider: str
        -fallback_providers: List~str~
        -_provider_map: AIProviderMap
        +__init__()
        -__initialize_providers() void
        +call_with_fallback(system_prompt, user_prompt) SelectionResponse
        +call_model(provider_name, **kwargs) Any
        +get_available_providers() List~str~
        +set_primary_provider(provider_name) bool
        +health_check() Dict~str, bool~
        +first_provider_name: str
    }
    
    class BaseAIProvider {
        <<abstract>>
        +call(**kwargs) Any
        +health_check() bool
    }
    
    class OpenAIProvider {
        +call(**kwargs) Any
        +health_check() bool
    }
    
    class AnthropicProvider {
        +call(**kwargs) Any  
        +health_check() bool
    }
    
    class DeepSeekProvider {
        +call(**kwargs) Any
        +health_check() bool
    }
    
    class AIProviderMap {
        -_provider_map: Dict
        +get_provider_class(provider_type) Type~BaseAIProvider~
        +register_provider(provider_type, provider_class) void
    }
    
    class AIModel {
        +provider: AIProviderEnum
        +config: Dict
    }
    
    AIManager --> BaseAIProvider: manages
    AIManager --> AIProviderMap: uses
    AIManager --> AIModel: configures
    BaseAIProvider <|-- OpenAIProvider
    BaseAIProvider <|-- AnthropicProvider  
    BaseAIProvider <|-- DeepSeekProvider
    AIProviderMap --> BaseAIProvider: creates
```

## 🔌 插件系统模块

### 插件管理核心类图

```mermaid
classDiagram
    class PluginManager {
        -discovery: PluginDiscovery
        -config: PluginConfig
        -loader: PluginLoader
        -registry: PluginRegistry
        -_running: bool
        +__init__()
        +start() void
        +reload() void
        +stop() void
        +call(plugin_id, method_name, **kwargs) Any
        +list_available_plugins() List~PluginRegistration~
        +get_plugin_info(plugin_id) PluginRegistration
        -_health_check_loop() void
    }
    
    class PluginDiscovery {
        +plugins: List~PluginResult~
        +start() void
        +discover_plugins(directory) List~PluginResult~
    }
    
    class PluginLoader {
        +load_plugin(plugin_result) PluginRegistration
        +validate_plugin(plugin_path) bool
    }
    
    class PluginRegistry {
        -_plugins: Dict~str, PluginRegistration~
        +register(plugin_registration) void
        +unregister(plugin_id) bool
        +list_plugins() List~str~
        +get_plugin(plugin_id) PluginRegistration
        +clean_all() void
    }
    
    class PluginRegistration {
        +plugin_id: str
        +name: str
        +version: str
        +description: str
        +status: PluginStatus
        +metadata: Dict
        +instance: Any
    }
    
    PluginManager --> PluginDiscovery: uses
    PluginManager --> PluginLoader: uses  
    PluginManager --> PluginRegistry: uses
    PluginRegistry --> PluginRegistration: stores
    PluginLoader --> PluginRegistration: creates
```

### 插件生命周期管理

```mermaid
classDiagram
    class PluginLifecycle {
        +initialize_plugin(plugin_path) PluginRegistration
        +start_plugin(plugin_id) bool
        +stop_plugin(plugin_id) bool
        +restart_plugin(plugin_id) bool
        +health_check(plugin_id) bool
    }
    
    class PluginValidator {
        +validate_structure(plugin_path) ValidationResult
        +validate_manifest(manifest_path) ValidationResult
        +validate_dependencies(requirements) ValidationResult
    }
    
    class ValidationResult {
        +success: bool
        +errors: List~str~
        +warnings: List~str~
    }
    
    PluginLifecycle --> PluginValidator: uses
    PluginValidator --> ValidationResult: returns
```

## 📋 任务处理模块

### 任务处理核心类图

```mermaid
classDiagram
    class TaskHandler {
        -db: DataBaseManager
        -step_service: StepHandler
        +__init__(db, step_service)
        +create_task_from_input(user_input, router, user_id) Dict
        +get_task_by_id(task_id) TaskDetailResponse
        +query_tasks(query: TaskQuery) PaginatedTaskResponse
        +delete_task(task_id) bool
        +update_task_status(task_id, status) bool
        -_save_task(task: Task) Task
        -_generate_steps(execution_plan, task_id) List~Step~
    }
    
    class StepHandler {
        -db: DataBaseManager
        +__init__(db)
        +create_steps(steps_data, task_id) List~Step~
        +get_steps_by_task_id(task_id) List~Step~
        +update_step_status(step_id, status) bool
        +delete_steps_by_task_id(task_id) bool
    }
    
    class TaskExecutor {
        -plugin_manager: PluginManager
        -step_handler: StepHandler
        +__init__(plugin_manager, step_handler)
        +execute_task(task_id) ExecutionResult
        +execute_step(step: Step) StepResult
        -_call_plugin(plugin_id, method, params) Any
    }
    
    class Task {
        +task_id: str
        +user_id: str
        +description: str
        +status: TaskStatus
        +created_at: datetime
        +updated_at: datetime
        +steps: List~Step~
    }
    
    class Step {
        +step_id: str
        +task_id: str
        +plugin_id: str
        +method_name: str
        +parameters: Dict
        +status: StepStatus
        +result: Dict
        +created_at: datetime
        +updated_at: datetime
    }
    
    TaskHandler --> StepHandler: uses
    TaskHandler --> Task: manages
    TaskExecutor --> StepHandler: uses
    TaskExecutor --> Step: executes
    Task --> Step: contains
```

### 任务状态管理

```mermaid
stateDiagram-v2
    [*] --> PENDING: 创建任务
    PENDING --> RUNNING: 开始执行
    RUNNING --> COMPLETED: 执行成功
    RUNNING --> FAILED: 执行失败
    RUNNING --> CANCELLED: 用户取消
    FAILED --> RUNNING: 重试执行
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

## 📡 MCP 协议模块

### MCP 通信类图

```mermaid
classDiagram
    class MCPServer {
        -plugin_manager: PluginManager
        +__init__(plugin_manager)
        +call(req: MCPRequestSchema) MCPResponseSchema
    }
    
    class MCPClient {
        +send_request(request) MCPResponseSchema
        +connect(endpoint) bool
        +disconnect() void
    }
    
    class MCPRequestSchema {
        +id: str
        +method: str
        +params: Dict
        +jsonrpc: str
    }
    
    class MCPResponseSchema {
        +id: str
        +result: Any
        +error: JSONRPCError
        +jsonrpc: str
        +success(result)$ MCPResponseSchema
        +fail(id, error)$ MCPResponseSchema
    }
    
    class JSONRPCError {
        +code: int
        +message: str
        +data: Any
        +internal_error(message)$ JSONRPCError
    }
    
    MCPServer --> MCPRequestSchema: receives
    MCPServer --> MCPResponseSchema: returns
    MCPClient --> MCPRequestSchema: sends
    MCPClient --> MCPResponseSchema: receives
    MCPResponseSchema --> JSONRPCError: contains
```

## 🌐 API 接口层

### API 路由类图

```mermaid
classDiagram
    class TaskRouter {
        +create_task_api(request, req, task_service, router) TaskCreateAPIResponse
        +get_task_api(task_id, task_service) TaskDetailResponse
        +query_tasks_api(query, task_service) PaginatedTaskResponse
        +delete_task_api(task_id, task_service) APIResponse
    }
    
    class MCPRouter {
        +list_plugins_api(mcp_service) PluginListResponse
        +call_plugin_api(request, mcp_service) PluginCallResponse
        +plugin_health_api(plugin_id, mcp_service) HealthResponse
    }
    
    class SystemRouter {
        +health_check_api() HealthResponse
        +system_info_api() SystemInfoResponse
        +metrics_api() MetricsResponse
    }
    
    class AIServerRouter {
        +list_providers_api(ai_manager) ProviderListResponse
        +call_ai_api(request, ai_manager) AICallResponse
        +set_primary_provider_api(request, ai_manager) APIResponse
    }
    
    class CreateTaskRequest {
        +user_input: str
    }
    
    class TaskCreateAPIResponse {
        +success: bool
        +data: TaskResult
        +message: str
    }
    
    TaskRouter --> CreateTaskRequest: uses
    TaskRouter --> TaskCreateAPIResponse: returns
```

## 🔧 配置管理模块

### 配置系统类图

```mermaid
classDiagram
    class Config {
        +load_config(config_path) Dict
        +get_section(section_name) Dict
        +validate_config() bool
    }
    
    class DatabaseConfig {
        +database_url: str
        +pool_size: int
        +echo: bool
        +create_engine() Engine
    }
    
    class AIConfig {
        +providers: List~AIModel~
        +default_provider: str
        +fallback_providers: List~str~
    }
    
    class PluginConfig {
        +plugin_directory: str
        +auto_discovery: bool
        +max_plugins: int
        +health_check_interval: int
    }
    
    class LoggingConfig {
        +level: str
        +format: str
        +handlers: List~str~
    }
    
    Config <|-- DatabaseConfig
    Config <|-- AIConfig
    Config <|-- PluginConfig
    Config <|-- LoggingConfig
```

## 🏗️ 依赖注入系统

### DI 容器类图

```mermaid
classDiagram
    class DIContainer {
        -_services: Dict~str, Any~
        -_singletons: Dict~str, Any~
        +register(service_type, implementation) void
        +register_singleton(service_type, implementation) void
        +resolve(service_type) T
        +get(service_name) Any
    }
    
    class Bootstrap {
        +configure_services(container: DIContainer) void
        +register_core_services(container) void
        +register_api_dependencies(container) void
    }
    
    class ServiceDescriptor {
        +service_type: Type
        +implementation: Type
        +lifetime: ServiceLifetime
    }
    
    Bootstrap --> DIContainer: configures
    DIContainer --> ServiceDescriptor: manages
```

## 📊 整体系统架构关系图

### 模块间依赖关系

```mermaid
graph TB
    subgraph API["🌐 API Layer"]
        TaskAPI[Task Router]
        MCPAPI[MCP Router] 
        AIAPI[AI Router]
        SysAPI[System Router]
    end
    
    subgraph Core["⚡ Core Layer"]
        subgraph Orchestration["编排引擎"]
            IntelligentRouter[IntelligentRouter]
            TaskPlanner[TaskPlanner]
        end
        
        subgraph Tasks["任务引擎"]
            TaskHandler[TaskHandler]
            StepHandler[StepHandler]
            TaskExecutor[TaskExecutor]
        end
        
        subgraph AI["AI引擎"]
            AIManager[AIManager]
            AIProviders[AI Providers]
        end
        
        subgraph Plugin["插件引擎"]
            PluginManager[PluginManager]
            PluginDiscovery[PluginDiscovery]
            PluginLoader[PluginLoader]
            PluginRegistry[PluginRegistry]
        end
        
        subgraph MCP["MCP协议"]
            MCPServer[MCPServer]
            MCPClient[MCPClient]
        end
    end
    
    subgraph Infrastructure["🔧 Infrastructure"]
        Config[Configuration]
        Database[Database]
        DI[DI Container]
        Logger[Logging]
    end
    
    %% API层依赖
    TaskAPI --> TaskHandler
    MCPAPI --> MCPServer
    AIAPI --> AIManager
    
    %% 核心业务流程
    TaskHandler --> IntelligentRouter
    IntelligentRouter --> TaskPlanner
    IntelligentRouter --> AIManager
    IntelligentRouter --> PluginManager
    TaskHandler --> StepHandler
    TaskExecutor --> PluginManager
    
    %% AI引擎
    TaskPlanner --> AIManager
    AIManager --> AIProviders
    
    %% 插件引擎
    PluginManager --> PluginDiscovery
    PluginManager --> PluginLoader
    PluginManager --> PluginRegistry
    PluginManager --> MCPServer
    MCPServer --> MCPClient
    
    %% 基础设施依赖
    TaskHandler --> Database
    StepHandler --> Database
    PluginRegistry --> Config
    AIManager --> Config
    
    %% DI注入
    DI -.-> TaskHandler
    DI -.-> AIManager
    DI -.-> PluginManager
    DI -.-> IntelligentRouter
```

## 🔍 架构优化建议

### 1. 潜在问题识别

**耦合度问题**：
- `IntelligentRouter` 直接依赖具体的 `PluginManager` 和 `AIManager`
- `TaskHandler` 与数据库层耦合较紧

**单一职责问题**：
- `PluginManager` 承担了太多职责（发现、加载、注册、调用）
- `AIManager` 同时管理配置和调用逻辑

### 2. 优化建议

**解耦建议**：
```mermaid
classDiagram
    class IPluginService {
        <<interface>>
        +listAvailablePlugins()
        +getPluginFunctions()
        +callPlugin()
    }
    
    class IAIService {
        <<interface>>
        +callWithFallback()
        +getAvailableProviders()
    }
    
    class IntelligentRouter {
        -pluginService: IPluginService
        -aiService: IAIService
    }
    
    IntelligentRouter --> IPluginService
    IntelligentRouter --> IAIService
```

**职责分离建议**：
- 将 `PluginManager` 拆分为 `PluginService` 和 `PluginLifecycleManager`
- 将 `AIManager` 拆分为 `AIConfigManager` 和 `AICallService`
- 引入 `Repository` 模式分离数据访问逻辑

### 3. 性能优化点

- 插件调用异步化
- AI Provider 连接池管理
- 任务执行状态缓存
- 配置热重载机制

---

*此文档基于当前代码结构生成，建议定期更新以保持同步。*