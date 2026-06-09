# AZ-400: Designing and Implementing Microsoft DevOps Solutions (Synthetic Certification Guide)

> SYNTHETIC DOCUMENT — Created for CRUCIBLE Enterprise hackathon demo. Not official Microsoft material.

## Exam Overview
- **Exam Code:** AZ-400
- **Level:** Expert
- **Recommended Study Hours:** 40–50 hours
- **Passing Score:** 700/1000
- **Target Audience:** DevOps engineers with advanced Azure administration and development experience
- **Prerequisite Certifications:** AZ-104 (Administrator) OR AZ-204 (Developer) must be earned first

## Skill Domains

### Domain 1: Design and Implement DevOps Processes (15–20%)
- **Design a DevOps strategy:** Source control strategy (GitFlow, trunk-based development), branching strategies, code review processes
- **Design and implement CI/CD pipelines:** Pipeline architecture, multi-stage YAML pipelines, pipeline templates, variable groups, environments
- **Implement infrastructure as code:** ARM templates, Bicep, Terraform on Azure, Pulumi, desired state configuration
- **Key concepts to defend:** Trade-offs between GitFlow and trunk-based development; how to design a pipeline strategy for microservices vs monoliths; when to use Bicep vs Terraform

### Domain 2: Design and Implement Source Control (10–15%)
- **Design a Git strategy:** Repository structure (mono-repo vs multi-repo), branch policies, pull request workflows, code review requirements
- **Manage Git at scale:** Git LFS for large files, submodules, subtree merges, repository permissions
- **Implement code quality gates:** Branch policies, required reviewers, build validation, status checks, merge strategies
- **Key concepts to defend:** How to enforce code quality through branch policies; when mono-repo is better than multi-repo; strategies for managing large binary files in Git

### Domain 3: Design and Implement Build and Release Pipelines (20–25%)
- **Configure pipeline agents:** Self-hosted vs Microsoft-hosted agents, agent pools, agent capabilities, container jobs
- **Design and implement CI pipelines:** Build triggers, parallel jobs, caching dependencies, artifact publishing, code coverage integration
- **Design and implement CD pipelines:** Deployment strategies (blue-green, canary, rolling), approval gates, deployment rings, feature flags
- **Implement package management:** Azure Artifacts, NuGet, npm, Maven, Python package feeds, upstream sources
- **Key concepts to defend:** How to implement canary deployments with Azure DevOps; the difference between blue-green and rolling deployments; when to use self-hosted agents vs Microsoft-hosted

### Domain 4: Design and Implement a Dependency Management Strategy (10–15%)
- **Manage dependencies:** Package versioning, semantic versioning, dependency scanning, vulnerability detection
- **Migrate and consolidate artifacts:** Artifact migration strategies, feed consolidation, upstream source configuration
- **Implement security scanning:** Dependency vulnerability scanning, container image scanning, SBOM generation
- **Key concepts to defend:** How semantic versioning prevents breaking changes; strategies for managing transitive dependencies; when to use upstream sources vs direct package references

### Domain 5: Design and Implement Application Infrastructure (15–20%)
- **Design infrastructure provisioning:** ARM/Bicep/Terraform templates, parameter files, environment-specific configurations, state management
- **Implement container infrastructure:** Azure Container Registry, Azure Kubernetes Service (AKS), Helm charts, Kustomize, container networking
- **Implement infrastructure monitoring:** Azure Monitor for containers, AKS diagnostics, container insights, log analytics
- **Key concepts to defend:** How to manage Terraform state in a team environment; AKS networking options (kubenet vs Azure CNI); strategies for zero-downtime AKS upgrades

### Domain 6: Design and Implement Continuous Feedback (10–15%)
- **Implement monitoring and alerting:** Application Insights, Azure Monitor, custom dashboards, alert rules, action groups
- **Implement feedback loops:** Release health monitoring, feature flag analytics, user feedback collection, incident management
- **Optimize telemetry:** Sampling strategies, custom telemetry, distributed tracing, performance baselines
- **Key concepts to defend:** How to design effective alert rules that reduce alert fatigue; the role of feature flags in continuous delivery; strategies for collecting and acting on user feedback

## Common Exam Topics
- CI/CD pipeline design for microservices architecture
- Infrastructure as Code best practices and state management
- Deployment strategies: blue-green vs canary vs rolling
- AKS deployment and management with Helm
- Security scanning integration in pipelines
- Azure DevOps vs GitHub Actions comparison

## Prerequisites
- AZ-104 (Azure Administrator) OR AZ-204 (Azure Developer) — must hold one
- 1+ years DevOps experience with Azure
- Proficiency with Git, CI/CD concepts, and infrastructure automation

## Study Pattern Recommendation
- Study 2–3 hours daily for 4–5 weeks
- Build end-to-end CI/CD pipelines for a sample application
- Practice with both Azure DevOps and GitHub Actions
- Take practice assessments after each domain
- Target 75%+ on practice tests before scheduling exam
