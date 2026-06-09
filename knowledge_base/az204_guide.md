# AZ-204: Developing Solutions for Microsoft Azure (Synthetic Certification Guide)

> SYNTHETIC DOCUMENT — Created for CRUCIBLE Enterprise hackathon demo. Not official Microsoft material.

## Exam Overview
- **Exam Code:** AZ-204
- **Level:** Associate
- **Recommended Study Hours:** 35–45 hours
- **Passing Score:** 700/1000
- **Target Audience:** Developers with 1–2 years of Azure development experience

## Skill Domains

### Domain 1: Develop Azure Compute Solutions (25–30%)
- **Implement IaaS solutions:** Create and configure VMs, VM scale sets, custom VM images, ARM/Bicep templates for VM deployment
- **Create Azure App Service Web Apps:** App Service plans, deployment methods (Git, ZIP, CI/CD), deployment slots, custom domains
- **Implement Azure Functions:** Triggers (HTTP, Timer, Blob, Queue, Event Grid), bindings (input, output), durable functions, function app settings
- **Develop for Azure Container Instances:** Container images, Dockerfile creation, container group configuration, volume mounts
- **Key concepts to defend:** When to use Azure Functions vs App Service vs VMs; how durable functions enable stateful serverless workflows; the trade-offs between consumption plan and premium plan for Functions

### Domain 2: Develop for Azure Storage (15–20%)
- **Implement Azure Cosmos DB storage:** Partition keys, consistency levels, request units (RUs), change feed, SDK operations
- **Implement blob storage solutions:** Blob types (block, append, page), access tiers, lifecycle management, SAS tokens, SDK operations
- **Implement Azure Table storage:** Entity design, partition and row keys, batch operations, SDK operations
- **Implement Azure Queue storage:** Message lifecycle, poison messages, visibility timeout, SDK operations
- **Key concepts to defend:** How to choose the right Cosmos DB consistency level for your use case; partition key selection strategies and their impact on throughput; when to use blob storage vs Table storage vs Cosmos DB

### Domain 3: Implement Azure Security (15–20%)
- **Implement user authentication and authorization:** Microsoft Entra ID authentication flows (OAuth 2.0, OpenID Connect), MSAL library, app registrations, API permissions
- **Implement secure cloud solutions:** Managed identities (system-assigned, user-assigned), Azure Key Vault (secrets, keys, certificates), Azure RBAC
- **Implement API Management security:** Subscription keys, OAuth, JWT validation, IP filtering, CORS policies
- **Key concepts to defend:** Difference between authentication and authorization in Entra ID; when to use managed identities vs service principals; how Key Vault rotation policies work; the flow of OAuth 2.0 authorization code grant

### Domain 4: Monitor, Troubleshoot, and Optimize Azure Solutions (10–15%)
- **Implement Azure Monitor:** Application Insights, custom metrics, log queries (KQL), alert rules, dashboards
- **Implement distributed tracing:** Application Insights dependency tracking, correlation IDs, end-to-end transaction diagnostics
- **Optimize solution performance:** Caching strategies (Azure Cache for Redis, CDN), auto-scaling, performance profiling
- **Key concepts to defend:** How to write effective KQL queries for log analysis; when to use Application Insights vs Azure Monitor metrics; caching strategies for different data access patterns

### Domain 5: Connect to and Consume Azure Services and Third-Party Services (20–25%)
- **Implement API Management:** Import APIs, policies (rate limiting, caching, transformation), products, subscriptions, developer portal
- **Develop for event-based solutions:** Event Grid (topics, subscriptions, event types), Event Hubs (throughput units, consumer groups, partitions), Service Bus (queues, topics, sessions, dead-lettering)
- **Develop for message-based solutions:** Service Bus vs Queue Storage comparison, message ordering, sessions, transactions
- **Key concepts to defend:** When to use Event Grid vs Event Hubs vs Service Bus; how Event Grid filtering works; Service Bus sessions and their use cases for ordered message processing

## Common Exam Topics
- Azure Functions triggers and bindings — which to use when
- Cosmos DB partition key design and its impact on performance
- Managed identities vs service principals — security implications
- Event Grid vs Event Hubs vs Service Bus — architectural decision matrix
- Application Insights instrumentation and KQL query patterns
- API Management policies for rate limiting and caching

## Prerequisites
- 1–2 years professional experience developing for Azure
- Proficiency in C#, Python, or JavaScript/TypeScript
- Recommended: AZ-900 or equivalent cloud fundamentals

## Study Pattern Recommendation
- Study 2 hours daily for 4 weeks
- Build hands-on projects for each domain (Functions app, Cosmos DB integration, API Management)
- Take practice assessments after each domain
- Target 75%+ on practice tests before scheduling exam
