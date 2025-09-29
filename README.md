# Nuwa - MCP插件管理平台

一个基于MCP（Model Context Protocol）协议的智能插件管理平台。

## 项目简介

Nuwa是一个现代化的插件管理平台，支持动态加载、管理和执行MCP服务插件。

## 快速开始

### 前置条件

1. Python 3.11+
2. node v20.x
3. npm v9.x

### 服务端启动

#### python

1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：`python main.py`
3. 访问API文档：`http://localhost:8000/docs`

#### conda

1. 创建环境：`conda create -n nuwa python=3.11`
2. 激活环境：`conda activate nuwa`
3. 安装依赖：`pip install -r requirements.txt`
4. 启动服务：`python main.py`

### 前端启动

1. 安装依赖：`npm install`
2. 启动服务：`npm start`

## 项目架构


```mermaid
graph TB
    %% 核心模块布局 - 2x2 网格
    subgraph CORE["🧠 Nuwa 核心架构"]
        direction TB
        
        %% 左上 - API网关
        API[🌐 API网关<br/>FastAPI + 路由<br/>中间件 + 模型]
        
        %% 右上 - AI智能中心
        AI[🤖 AI智能中心<br/>多模型支持<br/>智能路由决策]
        
        %% 左下 - MCP协议层
        MCP[🔌 MCP协议层<br/>服务器 + 客户端<br/>插件通信代理]
        
        %% 右下 - 插件系统
        PLUGIN[🔌 插件系统<br/>动态加载管理<br/>生命周期控制]
    end
    
    %% 任务编排引擎 - 中心节点
    ORCHESTRATION[🎭 任务编排引擎<br/>智能规划 + 执行调度]
    
    %% 外围支撑系统
    CONFIG[⚙️ 配置中心]
    DATA[💾 数据存储]
    
    %% 示例插件
    CAMERA[📹 Camera插件]
    PLUGIN-DEMO[📦 Plugin Demo]
    
    %% 核心数据流关系
    API --> AI
    AI --> ORCHESTRATION
    MCP --> PLUGIN
    PLUGIN --> ORCHESTRATION
    ORCHESTRATION --> MCP
    API --> ORCHESTRATION
    
    %% 配置和数据支撑
    CONFIG -.-> API
    CONFIG -.-> AI
    CONFIG -.-> MCP
    CONFIG -.-> PLUGIN
    
    DATA -.-> ORCHESTRATION
    
    %% 插件实例
    PLUGIN -.-> CAMERA
    PLUGIN -.-> PLUGIN-DEMO
    
    %% 样式定义
    classDef coreStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef centerStyle fill:#fff3e0,stroke:#f57c00,stroke-width:4px
    classDef supportStyle fill:#f5f5f5,stroke:#757575,stroke-width:2px
    classDef pluginStyle fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    
    class API,AI,MCP,PLUGIN coreStyle
    class ORCHESTRATION centerStyle
    class CONFIG,DATA supportStyle
    class CAMERA pluginStyle
    class PLUGIN-DEMO pluginStyle
```





