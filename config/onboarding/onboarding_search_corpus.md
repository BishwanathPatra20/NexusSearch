# Personalization KT — 10-day onboarding guide

Source: `Personalization_KT_Onboarding_10Day.xlsx` (imported for NexusSearch navigation and search).

Use this document to find Confluence pages, access groups, tickets, and day-by-day tasks.

## Day 1

### Day 1
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1253024861/Personalization+-+Team+Space

Theme / Focus: Team intro & platform vision
Activities & Tasks: Meet onboarding buddy; review team charter and org structure; read hexagonal architecture primer; skim Personalization Team Space.
Resources & Links: Team Space: https://confluence.sys.cigna.com/spaces/DEC/pages/1253024861/Personalization+-+Team+Space
Hexagonal Architecture: https://medium.com/ssense-tech/hexagonal-architecture-there-are-always-two-sides-to-every-story-bc0780ed7d9c
Deliverable / Exit Criteria: Can explain team vision and name key contacts (Eng, Data, QE, Product).
Suggested Owner: Team Lead / Buddy (Nagamohan)

## Day 2

### Day 2
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1339467463/Personalization+Platform

Theme / Focus: Platform design & use cases
Learning Objectives: Understand P360 purpose, conceptual/data flows, and major use case categories.
Activities & Tasks: Review Personalization Platform and Design pages; walk through Use Case Design child pages (Claim Status, AI Chatbot, Dashboard Insights POC).
Resources & Links: Platform: https://confluence.sys.cigna.com/spaces/DEC/pages/1339467463/Personalization+Platform
Design: https://confluence.sys.cigna.com/spaces/DEC/pages/1261308608/Personalization+-+Design
Use Cases: https://confluence.sys.cigna.com/pages/viewpage.action?pageId=1339467469
Deliverable / Exit Criteria: Can diagram high-level data sources (EVIR, EVFR, CDP, JourneyNet, SDI, AIE) and one end-to-end use case.
Suggested Owner: Product / EA Buddy (Nagamohan)

## Day 3

### Day 3
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1396411392/3+-+Intent+API

Theme / Focus: Intent API & contextual profile
Learning Objectives: Understand Intent API POC scope, Member Intent API, and Contextual/Profile API data model.
Activities & Tasks: Study Intent API HLD; review Contextual API fields and swagger; map APIs to myCigna consumption patterns.
Resources & Links: Intent API: https://confluence.sys.cigna.com/spaces/DEC/pages/1396411392/3+-+Intent+API
Contextual API: https://confluence.sys.cigna.com/spaces/DEC/pages/1284251927/2+-+Personalization+%2F+Contextual+API
Solution Architecture: https://confluence.sys.cigna.com/spaces/DEC/pages/1296871679/1+-+Solution+Architecture
Swagger: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-personalization-profile/-/blob/develop/swagger.yaml
Deliverable / Exit Criteria: Can describe Intent API POCs (CJA, IVR, JourneyNet, Verint) and list profile context categories.
Suggested Owner: API Engineer Buddy (Nagamohan)

## Day 4

### Day 4
- Category: ticket
- Ticket / request: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-personalization-profile

Theme / Focus: Backend architecture & Go services
Learning Objectives: Learn hexagonal architecture in practice, Go microservice patterns, and personalization-profile repo structure.
Activities & Tasks: Clone personalization-profile repo; review service layers (domain vs infrastructure); start Go microservices Pluralsight modules.
Resources & Links: Profile repo: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-personalization-profile
Go Microservices course (Pluralsight)
Go Testing course (Pluralsight)
Deliverable / Exit Criteria: Local repo builds; can navigate domain/infrastructure packages and explain one API handler flow.
Suggested Owner: Backend Buddy (Nagamohan)

## Day 5

### Day 5
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1729615717/Flink+Processing+Layer

Theme / Focus: Stream processing (Flink / Kinesis)
Learning Objectives: Understand real-time interaction pipeline, event grouping, LLM intent windows, and EVIR integration.
Activities & Tasks: Read Flink Processing Layer; review Kinesis interactions stream; discuss event canonical ID assumptions and enrichment needs.
Resources & Links: Flink Layer: https://confluence.sys.cigna.com/spaces/DEC/pages/1729615717/Flink+Processing+Layer
Flink Watermarks: https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/datastream/event-time/generating_watermarks/
Kinesis Connector: https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/connectors/datastream/kinesis/
Deliverable / Exit Criteria: Can explain Flink flow (ingest → enrich → window → LLM → global context store) and open questions.
Suggested Owner: Data / Stream Buddy (Nagamohan)

## Day 6

### Day 6
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1724269726/Personalization+Databricks+Connect+x+Cursor+IDE+Testing+Guide

Theme / Focus: Databricks & data pipelines
Learning Objectives: Set up Databricks Connect locally; understand Interactions-Databricks repo and environment config chain.
Activities & Tasks: Follow Cursor IDE Databricks setup; configure CLI profiles (dev/pvs/test); run LocalExplorer via sbt; review JourneyNet/Verint DBX jobs.
Resources & Links: Databricks Connect Guide: https://confluence.sys.cigna.com/spaces/DEC/pages/1724269726/Personalization+Databricks+Connect+x+Cursor+IDE+Testing+Guide
Cursor Setup: https://confluence.sys.cigna.com/spaces/DEC/pages/1730102044/Cursor+IDE+Databricks+Connect+Setup
Interactions DBX repo: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-perso-interactions-databricks/-/tree/next
Workspaces: en-edp-databricks-dev / en-edp-databricks-test
Deliverable / Exit Criteria: Successful sbt localDev/run (or localTest/run); understands Single User cluster requirement and app-{env}.conf chain.
Suggested Owner: Data Engineer Buddy (Nagamohan)

## Day 7

### Day 7
- Category: ticket
- Ticket / request: https://auth0.com/docs/deploy-monitor/logs

Theme / Focus: Auth, IAM & identity patterns
Learning Objectives: Understand M2M tokens, Auth0/IAM integration, PBC identity resolution, and multi-tenant considerations.
Activities & Tasks: Review Auth0 log types; trace getPersonalizationM2mToken in Cypress support code; study SSOID/IEID/PRID identifier types.
Resources & Links: Auth0 Logs: https://auth0.com/docs/deploy-monitor/logs
Auth0 Log Catalog: https://auth0.com/docs/logs/log-data-type-reference
EVIR Integration: https://confluence.sys.cigna.com/spaces/DEC/pages/1428297144/EVIR+Integration
Deliverable / Exit Criteria: Can obtain M2M token and explain primaryUserIdType enums used by Interactions/Insights APIs.
Suggested Owner: Security / IAM Buddy (Nagamohan)

## Day 8

### Day 8
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1838812489/Personalization+API+%E2%80%93+QA+Automation+Handover

Theme / Focus: Cypress QA automation overview
Learning Objectives: Learn Cypress API test structure, fixtures, gateway env vars, and personalization test coverage.
Activities & Tasks: Read QA Automation Handover; explore cypress/pbc/integration/personalization specs and shared API clients; review swagger alignment.
Resources & Links: QA Handover: https://confluence.sys.cigna.com/spaces/DEC/pages/1838812489/Personalization+API+%E2%80%93+QA+Automation+Handover
QA Details: https://confluence.sys.cigna.com/spaces/DEC/pages/1838812491/Personalization+API+%E2%80%93+QA+Automation
Cypress Why: https://docs.cypress.io/app/get-started/why-cypress
QE Monorepo: https://git.sys.cigna.com/digital-experience/qe/monorepo/-/tree/NS/personalization-api
Cypress Dashboard: Reporting O_CypressCloudDigitalEng_Member
Deliverable / Exit Criteria: Can locate all 7 personalization spec files and explain Interactions vs Insights vs $search coverage.
Suggested Owner: QE Buddy (Nagamohan)

## Day 9

### Day 9
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1838814241/CI+Pipeline+Runbook+%28API+Trigger%29

Theme / Focus: Run tests locally & CI pipeline
Learning Objectives: Execute personalization regression locally; trigger GitLab CI job; understand Webex/MS Team reporting.
Activities & Tasks: yarn install in cypress/; run suite against SIT; trigger personalization-regression pipeline; review CI runbook variables.
Resources & Links: CI Runbook: https://confluence.sys.cigna.com/spaces/DEC/pages/1838814241/CI+Pipeline+Runbook+%28API+Trigger%29
Local run: yarn cy run -P pbc -C cypress.enapp.sit.config.ts
Webex room: Personalization - Automation Results
MS Team Channel: personlization-automation-reports
Deliverable / Exit Criteria: Local run completed; CI trigger payload understood; knows PBC_API_ENV, PBC_GATEWAY, E2E_ENV settings.
Suggested Owner: QE Buddy (Nagamohan)

## Day 10

### Day 10
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1261308610/Personalization+-+Delivery

Theme / Focus: Integration & first contribution
Learning Objectives: Consolidate learning; pair on a small task; plan first PR; document gaps.
Activities & Tasks: Shadow stand-up/sprint; pair on bug/fixture/test; review open PRs; update onboarding checklist; pick first story.
Resources & Links: Delivery page: https://confluence.sys.cigna.com/spaces/DEC/pages/1261308610/Personalization+-+Delivery
Jira label: digital-personalization
Deliverable / Exit Criteria: First contribution identified; onboarding checklist 80%+ complete; KT sign-off with buddy.
Suggested Owner: Team Lead / Buddy (Nagamohan)

## General

### Project
- Category: general

Unnamed: 1: Personalization Platform (P360) — Digital Experience / PBC

### Team Space
- Category: ticket
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1253024861/Personalization+-+Team+Space

### Duration
- Category: general

Unnamed: 1: 10 business days (compressed from ONBOARDING_PLAN.md)

### Audience
- Category: general

Unnamed: 1: New joiners — Engineering, Data, QE

### Last Updated
- Category: general

Unnamed: 1: August 2026

### Source Docs
- Category: general

Unnamed: 1: Confluence DEC space, Learning Plan, QA Automation Handover

### Platform Mission
- Category: general

### Drive enterprise-wide personalization via foundational capabilities that provide efficient access to actionable user data/models and power personalized communications, patient journeys, and recommendations across the Cigna ecosystem.

Three core questions:
1. What is a user's intent at any given time?
2. What is the Cigna Group's primary intent for that user?
3. What, when, and how do we communicate to a user?
- Category: general

### Sheet Guide
- Category: general

### 10-Day KT Plan
- Category: general

Unnamed: 1: Day-by-day schedule with objectives, activities, resources, deliverables

### Confluence Resources
- Category: general

Unnamed: 1: Curated links from team Confluence pages

### Repositories
- Category: general

Unnamed: 1: Key GitLab repos and branches

### Cypress Testing
- Category: general

Unnamed: 1: API test specs, coverage, fixtures

### Cypress Env & CI
- Category: general

Unnamed: 1: Environment variables, gateway URLs, CI trigger settings

### Databricks
- Category: general

Unnamed: 1: Local Connect setup, workspaces, troubleshooting

### Onboarding Checklist
- Category: general

Unnamed: 1: Trackable checklist with target days

### Team
- Category: team
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1253024861/Personalization+-+Team+Space

Team vision, org chart, calendar, charter links

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1261308608/Personalization+-+Design

Parent for platform, use cases, Databricks guide, EVIR

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1339467463/Personalization+Platform

Three platform questions; conceptual & detailed views; data sources

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/pages/viewpage.action?pageId=1339467469

Claim Status, AI Chatbot, CareNav, EMBRACE, Dashboard Insights POC

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1396411392/3+-+Intent+API

Intent HLD, POCs (CJA, IVR, JourneyNet, Verint), taxonomy

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1296871679/1+-+Solution+Architecture

Capability mapping and platform design diagrams

### Design
- Category: design
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1284251927/2+-+Personalization+%2F+Contextual+API

Profile fields, data sources, swagger, gateway access

### Data
- Category: data
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1729615717/Flink+Processing+Layer

Real-time interactions, Kinesis, LLM windowing, EVIR

### Data
- Category: data
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1724269726/Personalization+Databricks+Connect+x+Cursor+IDE+Testing+Guide

Local Spark via Databricks Connect; sbt localDev/localTest

### Data
- Category: data
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1730102044/Cursor+IDE+Databricks+Connect+Setup

Extension setup, cluster creation via CI pipeline

### Delivery
- Category: delivery
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1261308610/Personalization+-+Delivery

Phase 1-3 roadmap, work streams, release timeline

### Delivery
- Category: delivery
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1339467471/Claim+Status

Claims call reduction; AIE → EVFR → P360 → myCigna flow

### QA
- Category: qa
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1838812491/Personalization+API+%E2%80%93+QA+Automation

Spec list, env vars, known issues, handover checklist

### QA
- Category: qa
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1838814241/CI+Pipeline+Runbook+%28API+Trigger%29

GitLab trigger payload, MS Teams setup, Cypress Cloud vars

### Authentication / M2M
- Category: authentication_/_m2m
- Ticket / request: https://confluence.sys.cigna.com/spaces/DEC/pages/1939206219/End-to-end+onboard+a+consumer+in+auth-admin-dev+get+a+bearer+token+call+your+API

M2M consumer onboarding, token, and API access in dev.

### digexp-pbc-personalization-profile
- Category: ticket
- Ticket / request: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-personalization-profile

Purpose: Core Personalization / Context Profile API (Interactions, Insights, $search, Clinical)
Key Branch / Notes: develop — swagger.yaml is source of truth for API contracts

### digexp-pbc-perso-interactions-databricks
- Category: ticket
- Ticket / request: https://git.sys.cigna.com/digital-experience/pbc/personalization/digexp-pbc-perso-interactions-databricks

Purpose: Interactions pipeline DBX jobs, cluster CI, LocalExplorer.scala for Databricks Connect
Key Branch / Notes: next — Single User clusters per developer per env

### QE Monorepo (Personalization Cypress)
- Category: ticket
- Ticket / request: https://git.sys.cigna.com/digital-experience/qe/monorepo/-/tree/NS/personalization-api

Purpose: Cypress API automation for PBC Personalization domain
Key Branch / Notes: NS/personalization-api — specs under cypress/pbc/integration/personalization/

### Personalisation Repos
- Category: ticket
- Ticket / request: https://git.sys.cigna.com/digital-experience/pbc/personalization

Purpose: All Personalization Use Cases Repos
Key Branch / Notes: depends on each Repo

### interactions.spec.ts
- Category: general

interactionType enum: PROVIDER_SEARCHES, CLAIM_INTERACTIONS; primaryUserIdType: SSOID, IEID

### insights.spec.ts
- Category: general

Parametric cases with test IDs (INS-xxx)

### claim-insights-get.spec.ts
- Category: general

Uses ami| prefixed identifiers

### preventiveCareNudges.spec.ts
- Category: general

API / Endpoint: POST /v1/profile/insights/$search/preventiveCareNudges
Coverage Summary: Request/response schema, validation scenarios
Test Data Location: fixtures/data/personalization/preventive-care-nudges-cases.ts

### loginState.spec.ts
- Category: general

API / Endpoint: POST /v1/profile/insights/$search/loginState
Coverage Summary: IEID/PRID cases, failure reasons, timestamp validation (LS_001–013)
Test Data Location: fixtures/data/personalization/login-state-cases.ts, login-state-ids.ts

### recentVendors.spec.ts
- Category: general

API / Endpoint: POST /v1/profile/insights/$search/recentVendors
Coverage Summary: Recent vendor search insights
Test Data Location: fixtures/data/personalization/recent-vendors-cases.ts

### providerOutOfNetwork.spec.ts
- Category: general

API / Endpoint: POST /v1/profile/insights/$search/providerOutOfNetwork
Coverage Summary: Out-of-network provider insights
Test Data Location: fixtures/data/personalization/provider-out-network-cases.ts

### PBC_API_ENV
- Category: general

Selects gateway environment URLs

### PBC_GATEWAY
- Category: general

Gateway routing (default: express)

### E2E_APP
- Category: general

Cypress project folder

### E2E_ENV
- Category: general

Config file suffix (NOT cypress.enapp.sit.config.ts)

### CI_RUN_TYPE
- Category: general

GitLab CI job mapping key

### E2E_SPECS_TO_RUN
- Category: general

Optional single-spec override

### E2E_DISABLE_PARALLEL
- Category: general

Recommended for single-node runs

### SKIP_REPORTER_JOB
- Category: general

Skip separate reporter job; inline MS Teams post runs after tests on node 1

### CYPRESS_MSTEAMS_SEND_NOTIFICATION
- Category: general

Enable MS Teams reporting (result-post.ts)

### CYPRESS_MSTEAMS_NOTIFICATION_TITLE
- Category: general

Title shown in Teams message

### CYPRESS_MSTEAMS_SEND_ONLY_FAILURE
- Category: general

When true, notify only on test failures

### CYPRESS_PROJECT_ID
- Category: general

Cypress Cloud project (optional) Global Group: O_CypressCloudDigitalEng_Member

### GitLab CI Variables (set once — never in trigger payload)
- Category: general

### Variable
- Category: general

Description

### UC_CYPRESS_RECORD_KEY
- Category: general

Cypress Cloud record key

### CYPRESS_MSTEAMS_WEBHOOK_URL
- Category: general

MS Teams incoming webhook URL for results channel

### CYPRESS_MSTEAMS_CHANNEL_NAME
- Category: general

Alternative: channel name mapped in msteams-channel-mapper.ts

### Reporting Flow
- Category: general

### 1. after:run hook
- Category: general

Example Value: Writes pbc/json-report/summary-*.json per CI node

### 2. Suite runner (node 1)
- Category: general

Example Value: Runs yarn ts-node scripts/result-post.ts after Cypress completes

### 3. result-post.ts
- Category: general

Example Value: Merges JSON reports and posts HTML summary to MS Teams webhook

### 4. Parallel runs
- Category: general

Example Value: Only CI_NODE_INDEX=1 posts; other nodes skip reporting

### Gateway URLs
- Category: general

### Gateway
- Category: general

Base URL

### express
- Category: ticket
- Ticket / request: https://internalapi-dev.express-scripts.io/pbc/personalization

https://internalapi-dev.express-scripts.io/pbc/personalization

### express
- Category: ticket
- Ticket / request: https://internalapi-qa.express-scripts.io/pbc/personalization

https://internalapi-qa.express-scripts.io/pbc/personalization

### express
- Category: ticket
- Ticket / request: https://internalapi.express-scripts.io/pbc/personalization

https://internalapi.express-scripts.io/pbc/personalization

### evernorth
- Category: ticket
- Ticket / request: https://api-dev.aws.internal.evernorth.io/pbc/personalization

https://api-dev.aws.internal.evernorth.io/pbc/personalization

### evernorth
- Category: ticket
- Ticket / request: https://api-qa.aws.internal.evernorth.io/pbc/personalization

https://api-qa.aws.internal.evernorth.io/pbc/personalization

### evernorth
- Category: ticket
- Ticket / request: https://api-uat.internal.evernorth.io/pbc/personalization

https://api-uat.internal.evernorth.io/pbc/personalization

### Workspaces
- Category: ticket
- Ticket / request: https://en-edp-databricks-dev.cloud.databricks.com

DEV: https://en-edp-databricks-dev.cloud.databricks.com
TEST: https://en-edp-databricks-test.cloud.databricks.com

### Prerequisites
- Category: general

Java 17 (Temurin); SBT 1.10.x+; Databricks CLI with PAT; Single User cluster per dev per env

### Repo
- Category: general

digexp-pbc-perso-interactions-databricks (branch: next)

### Local run commands
- Category: general

Dev: sbt localDev/run
PVS: sbt localPvs/run
Test: sbt localTest/run

### Config chain
- Category: general

DATABRICKS_CONFIG_PROFILE env var → ~/.databrickscfg → app/app-{env}.conf (S3, Kafka, etc.)

### Explorer file
- Category: general

LocalExplorer.scala — shared across envs; edit for queries/mapper testing

### Cluster requirement
- Category: general

Single User access mode only (Shared clusters incompatible with Databricks Connect)

### Runtime version
- Category: general

Databricks Connect 17.3.x must match cluster runtime; add to build.sbt

### Intent API POCs using DBX
- Category: general

JourneyNet Embeddings DBX jobs; Verint call transcripts/summaries from contact center analytics

### Cursor extension
- Category: general

Install Databricks extension; create config; setup Python venv with databricks-connect

### Common errors
- Category: general

Java 23 incompatibility → use Java 17; NoClassDefFoundError → check build.sbt deps; cluster timeout → verify PAT and Single User mode

### 1
- Category: team

Checklist Item: Meet team and onboarding buddy
Target Day: Day 1

### 2
- Category: architecture

Checklist Item: Read Personalization Team Space & platform vision
Target Day: Day 1

### 3
- Category: architecture

Checklist Item: Understand hexagonal architecture principles
Target Day: Day 1

### 4
- Category: architecture

Checklist Item: Review Personalization Platform & Use Case Design
Target Day: Day 2

### 5
- Category: architecture

Checklist Item: Study Intent API and contextual profile APIs
Target Day: Day 3

### 6
- Category: repos

Checklist Item: Clone digexp-pbc-personalization-profile repo
Target Day: Day 4

### 7
- Category: repos

Checklist Item: Build/run profile API locally
Target Day: Day 4

### 8
- Category: data

Just to understand real time streaming using Flink

### 9
- Category: databricks

in the readme docs and Buddy will help

### 10
- Category: databricks

Raised access to GGs

### 11
- Category: databricks

Checklist Item: Obtain Single User Databricks cluster access
Target Day: Day 6

### 12
- Category: security
- Ticket / request: https://auth-admin-dev.express-scripts.com/home

https://auth-admin-dev.express-scripts.com/home

### 13
- Category: security

Work done by See Long and Van

### 14
- Category: qa

Checklist Item: Clone QE monorepo (NS/personalization-api branch)
Target Day: Day 8

### 15
- Category: qa

Checklist Item: Review all 7 personalization Cypress specs
Target Day: Day 8

### 16
- Category: qa

yarn cy run -P pbc -C cypress.enapp.sit.config.ts

### 17
- Category: qa

Checklist Item: Trigger CI pipeline (personalization-regression)
Target Day: Day 9

### 18
- Category: qa

Checklist Item: Add WebHook to MS channel or verify notifications
Target Day: Day 9

### 19
- Category: delivery

LoginState Usecase both Dev & QA (Shadow Work)

### 20
- Category: delivery

Checklist Item: Identify first contribution (bug/feature/test)
Target Day: Day 10

### 21
- Category: team

Checklist Item: Attend sprint planning / stand-up
Target Day: Day 10

### 22
- Category: team

Checklist Item: KT sign-off with buddy and team lead
Target Day: Day 10

### Project Account Detials
- Category: confluence
- Confluence: https://cignatlp-my.sharepoint.com/:x:/r/personal/c9g3tj_glbcore_com/Documents/p360_account_details.xlsx?d=w8c6f263a981149999cca52ad0ea1fe8d&csf=1&web=1&e=pskQ2K

### Auth Admin
- Category: auth_admin
- Access / global group: G_AUTH_ADMIN_PROD_GA.[INTERNAL]

Required for prod API auth and protected resource access

### Auth Admin
- Category: auth_admin
- Access / global group: G_AUTH_ADMIN_NONPROD_GA.[INTERNAL]

Required for SIT/dev Cypress M2M token and API testing

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-DEV_ACCOUNTADMIN

Typically not needed for standard developers

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-DEV_DEVELOPER

Core dev environment access

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-DEV_DIGITALDEVELOPER

Standard role for digital/PBC team members

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-TEST_DEVELOPER

Needed for SIT testing and deployments

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-TEST_DIGITALDEVELOPER

Standard test environment access

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-PROD_DEVELOPER

Request after onboarding; prod changes require approval

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-PROD_READONLYACCESS

Safe prod visibility without write access

### AWS — Digital Experience
- Category: aws_—_digital_experience
- Access / global group: G_AWS_DIGEXP-TEST_READONLYACCESS

Useful for QE troubleshooting and log review

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: G_DATABRICKS_DIGEXP_DEV_DEVELOPER

Workspace: en-edp-databricks-dev.cloud.databricks.com

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: G_DATABRICKS_DIGEXP_TEST_DEVELOPER

Workspace: en-edp-databricks-test.cloud.databricks.com

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: G_DATABRICKS_DIGEXP_PROD_DEVELOPER

Request after onboarding completion

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: O_DATABRICKS_DIGEXP_DEV_DEVELOPER

Optional for G Databricks

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: O_DATABRICKS_DIGEXP_TEST_DEVELOPER

Optional for G Databricks

### Databricks — Digital Experience
- Category: databricks_—_digital_experience
- Access / global group: O_DATABRICKS_DIGEXP_PROD_DEVELOPER

Optional for G Databricks

### GitHub — Internal
- Category: github_—_internal
- Access / global group: G_GITHUB_SAAS_ACCESS.[INTERNAL]

Required for GitLab/GitHub repo access

### Health Services
- Category: health_services
- Access / global group: GitHubEnterpriseDeveloper

Needed for digital-experience GitLab repos

### Okta — Learning & Tools
- Category: okta_—_learning_&_tools
- Access / global group: O_PLURALSIGHTLEARNING_USERS

See ONBOARDING_PLAN.md course links

### Okta — Learning & Tools
- Category: okta_—_learning_&_tools
- Access / global group: O_COPILOT_ALLOW

Optional productivity tool

### Okta — Learning & Tools
- Category: okta_—_learning_&_tools
- Access / global group: O_CURSOR_MEMBER

Required for Databricks Connect + Cursor setup

### Okta — Learning & Tools
- Category: okta_—_learning_&_tools
- Access / global group: O_GITHUB_COPILOT_ACCESS

Optional

### Okta — Learning & Tools
- Category: okta_—_learning_&_tools
- Access / global group: O_GITHUB_SAAS_ACCESS

Complements G_GITHUB_SAAS_ACCESS global group

### AWS Federation
- Category: aws_federation
- Access / global group: AWS_USER_AUTO_FEDERATION

Prerequisite for all G_AWS_DIGEXP-* groups

### Cypress Cloud
- Category: cypress_cloud
- Access / global group: O_CypressCloudDigitalEng_Member

Standard Cypress Cloud access

### GitLab — Internal
- Category: gitlab_—_internal
- Access / global group: G_TEAM_DIGITAL-PERSONALIZATION

Workspace: GitLab Access

### How to request: Submit global group requests via Cigna Medical (AWS, Databricks, Auth Admin, GitHub Internal) or Health Services (GitHubEnterpriseDeveloper). Okta apps are assigned separately. Ask onboarding buddy or team lead for RITM/template if unsure. Track status in Request Status column.
- Category: access
