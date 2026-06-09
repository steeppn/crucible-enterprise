# AZ-104: Microsoft Azure Administrator (Synthetic Certification Guide)

> SYNTHETIC DOCUMENT — Created for CRUCIBLE Enterprise hackathon demo. Not official Microsoft material.

## Exam Overview
- **Exam Code:** AZ-104
- **Level:** Associate
- **Recommended Study Hours:** 30–40 hours
- **Passing Score:** 700/1000
- **Target Audience:** Azure administrators with 6+ months of hands-on experience

## Skill Domains

### Domain 1: Manage Azure Identities and Governance (20–25%)
- **Manage Microsoft Entra ID (Azure AD) users and groups:** Create users, manage group membership, bulk operations, guest users
- **Manage user and group properties:** Password reset policies, profile information, custom attributes
- **Manage licenses in Microsoft Entra ID:** Assign licenses, manage groups with dynamic membership for licensing
- **Manage external identities:** B2B collaboration, B2B direct connect, guest user access
- **Configure Entra ID roles and administrative units:** Built-in roles, custom roles, role assignments, scope limitations
- **Manage subscriptions and governance:** Management groups, Azure Policy initiatives, resource locks, tags, Azure Blueprints
- **Key concepts to defend:** Difference between built-in and custom roles; how Azure Policy enforces compliance vs RBAC controlling access; when to use management groups vs resource groups

### Domain 2: Implement and Manage Storage (15–20%)
- **Configure access to storage:** Storage account keys, SAS tokens, shared access signatures, managed identities, Azure AD integration
- **Configure and manage storage accounts:** Create storage accounts, configure replication (LRS, ZRS, GRS, RA-GRS), manage access tiers (hot, cool, archive)
- **Configure Azure Files and Azure Blob Storage:** File shares, blob containers, lifecycle management policies, soft delete
- **Manage storage security:** Network rules, private endpoints, encryption at rest, customer-managed keys
- **Key concepts to defend:** When to use SAS vs managed identities for storage access; difference between ZRS and GRS replication; how lifecycle management reduces costs

### Domain 3: Deploy and Manage Azure Compute Resources (20–25%)
- **Automate VM deployment:** ARM templates, Bicep, Azure CLI, PowerShell, Azure Portal
- **Create and configure virtual machines:** VM sizes, availability sets, availability zones, VM scale sets
- **Configure VM networking:** Network interfaces, NSGs, public IPs, private endpoints
- **Manage VM storage:** OS disks, data disks, managed disks, disk encryption, disk performance tiers
- **Deploy and configure Azure Container Instances:** Container groups, environment variables, volume mounts
- **Deploy and configure Azure App Service:** App Service plans, deployment slots, custom domains, TLS/SSL certificates
- **Key concepts to defend:** When to use VM scale sets vs individual VMs; how deployment slots enable zero-downtime deployments; difference between availability sets and availability zones

### Domain 4: Configure and Manage Virtual Networking (20–25%)
- **Configure virtual networks:** Address spaces, subnets, service endpoints, private endpoints
- **Configure name resolution:** Azure DNS zones, custom DNS, private DNS zones
- **Configure network security:** NSG rules, Azure Firewall, DDoS protection, WAF on Application Gateway
- **Configure load balancing:** Azure Load Balancer (L4), Application Gateway (L7), Traffic Manager, Front Door
- **Configure hybrid connectivity:** Site-to-Site VPN, Point-to-Site VPN, ExpressRoute, VPN Gateway types
- **Key concepts to defend:** When to use Application Gateway vs Load Balancer; how ExpressRoute differs from VPN Gateway; the purpose of private DNS zones in hybrid scenarios

### Domain 5: Monitor and Maintain Azure Resources (10–15%)
- **Monitor resources with Azure Monitor:** Metrics, logs, Log Analytics workspaces, alert rules
- **Configure diagnostic settings:** Resource logs, platform logs, activity logs, log export
- **Implement backup and recovery:** Azure Backup vault, Recovery Services vault, backup policies, restore procedures
- **Key concepts to defend:** Difference between metrics and logs in Azure Monitor; when to use Azure Backup vs site-level backup; how alert rules reduce mean time to detection

## Common Exam Topics
- RBAC vs Azure Policy — when to use each
- Storage replication options and their RPO/RTO implications
- VM sizing and cost optimization strategies
- VNet peering vs VPN Gateway vs ExpressRoute
- Azure Monitor alert rule configuration and action groups

## Prerequisites
- 6+ months hands-on Azure administration experience
- Recommended: AZ-900 or equivalent knowledge

## Study Pattern Recommendation
- Study 2 hours daily for 3–4 weeks
- Hands-on labs for each domain are essential
- Take practice assessments after each domain
- Target 75%+ on practice tests before scheduling exam
