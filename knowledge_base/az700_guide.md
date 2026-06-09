# AZ-700: Designing and Implementing Microsoft Azure Networking Solutions (Synthetic Certification Guide)

> SYNTHETIC DOCUMENT — Created for CRUCIBLE Enterprise hackathon demo. Not official Microsoft material.

## Exam Overview
- **Exam Code:** AZ-700
- **Level:** Associate
- **Recommended Study Hours:** 30–40 hours
- **Passing Score:** 700/1000
- **Target Audience:** Network engineers with experience designing and implementing Azure networking solutions

## Skill Domains

### Domain 1: Design and Implement Hybrid Networking (20–25%)
- **Design hybrid connectivity solutions:** Site-to-Site VPN, Point-to-Site VPN, ExpressRoute, ExpressRoute Direct
- **Compare connectivity options:** VPN Gateway vs ExpressRoute (cost, bandwidth, latency, SLA, use cases)
- **Design ExpressRoute architecture:** Peering types (Microsoft, Private, Public), ExpressRoute Gateway, FastPath, Global Reach
- **Implement hybrid DNS:** Azure DNS, custom DNS servers, conditional forwarding, DNS resolution across hybrid environments
- **Key concepts to defend:** When to choose ExpressRoute over VPN Gateway; how ExpressRoute peering types differ; DNS resolution challenges in hybrid environments and their solutions

### Domain 2: Design and Implement Azure Virtual Networks (20–25%)
- **Design VNet architecture:** Address space planning, subnet design, service endpoints, private endpoints, VNet peering
- **Implement VNet peering:** Gateway transit, remote gateways, peering limitations, cross-subscription peering, cross-tenant peering
- **Configure network security:** Network Security Groups (NSGs), application security groups (ASGs), service tags, NSG flow logs
- **Implement IP addressing:** Public IPs, private IPs, IP planning, NAT Gateway, outbound connectivity patterns
- **Key concepts to defend:** VNet peering limitations (non-transitive, same region vs global); when to use private endpoints vs service endpoints; NSG rule processing order and best practices

### Domain 3: Design and Implement Azure Load Balancing and Routing (20–25%)
- **Design load balancing solutions:** Azure Load Balancer (L4), Application Gateway (L7), Traffic Manager, Front Door, CDN
- **Compare load balancers:** When to use each load balancer type, feature comparison, cost considerations
- **Implement Application Gateway:** WAF policies, URL-based routing, path-based routing, SSL termination, autoscaling
- **Implement Front Door:** Routing rules, caching, WAF, custom domains, SSL certificates, health probes
- **Implement Traffic Manager:** Routing methods (priority, weighted, performance, geographic, multi-value), endpoint monitoring
- **Key concepts to defend:** Application Gateway vs Front Door — when to use each; WAF rule customization and exclusions; Traffic Manager routing method selection criteria

### Domain 4: Design and Implement Network Security (15–20%)
- **Design network security architecture:** Defense in depth, network segmentation, zero-trust networking, micro-segmentation
- **Implement Azure Firewall:** Firewall policies, rule collections (NAT, network, application), threat intelligence, DNS proxy, forced tunneling
- **Implement DDoS protection:** DDoS Protection Basic vs Standard, DDoS protection plans, monitoring and alerting
- **Implement Web Application Firewall:** OWASP rules, custom rules, managed rules, exclusion lists, logging and monitoring
- **Key concepts to defend:** Azure Firewall vs NSG — when to use each; DDoS Standard protection features beyond Basic; WAF rule tuning to reduce false positives

### Domain 5: Design and Implement Private Access to Azure Services (10–15%)
- **Implement private endpoints:** Private DNS zones, private link service, private endpoint connections, regional limitations
- **Implement Azure Private Link:** Supported services, cross-tenant private link, private link hub
- **Design private access architecture:** Hub-spoke with private endpoints, private DNS resolution, network routing considerations
- **Key concepts to defend:** Private endpoint vs service endpoint — security implications; private DNS zone configuration for private endpoints; limitations and workarounds for cross-region private endpoints

## Common Exam Topics
- ExpressRoute vs VPN Gateway decision matrix
- VNet peering design and limitations
- Application Gateway vs Front Door vs Traffic Manager comparison
- Azure Firewall rule configuration and policy management
- Private endpoint implementation and DNS configuration
- Load balancer health probes and backend pool configuration

## Prerequisites
- Strong understanding of networking concepts (TCP/IP, DNS, routing, firewalls)
- 1+ years experience with Azure networking
- Recommended: AZ-104 or equivalent Azure administration knowledge

## Study Pattern Recommendation
- Study 2 hours daily for 3–4 weeks
- Hands-on labs for VNet peering, ExpressRoute simulation, Application Gateway, and Azure Firewall
- Take practice assessments after each domain
- Target 75%+ on practice tests before scheduling exam
