# DataStage Pipeline Documentation Assistant
## Requirements Document & Kanban Delivery Blueprint

**Project Duration:** 6-8 weeks (Kanban-style continuous delivery)  
**Role:** Junior AI Analyst  
**Last Updated:** October 22, 2025

---

## 1. Executive Summary

This project develops an AI-powered assistant that automatically generates and maintains documentation for IBM DataStage ETL pipelines. The tool analyzes DataStage job exports (DSX files), extracts logic and metadata, and produces human-readable documentation including data lineage, transformation logic, and operational guides.

**Value Proposition:**
- Reduce documentation time from 4-6 hours per job to 15-30 minutes
- Maintain living documentation that evolves with pipeline changes
- Improve knowledge transfer and reduce onboarding time by 50%
- Enable non-technical stakeholders to understand data flows
- Create searchable knowledge base of all pipeline logic

**Delivery Approach:** Kanban-style incremental delivery with continuous value realization. Each feature is delivered to production as soon as it's ready, allowing the team to start benefiting immediately while subsequent features are developed.

---

## 2. Project Objectives

### Primary Objectives
1. Build a tool that parses DataStage DSX files and extracts job metadata
2. Generate comprehensive documentation in multiple formats (Markdown, HTML, PDF)
3. Implement AI-powered natural language descriptions of transformation logic
4. Create interactive documentation with searchable content
5. Enable continuous documentation updates as pipelines evolve

### Secondary Objectives
1. Build a conversational interface to query pipeline documentation
2. Generate data lineage diagrams automatically
3. Identify and document pipeline dependencies
4. Create operational runbooks from job configurations
5. Integrate with team's existing documentation platform

---

## 3. Kanban Delivery Model

### 3.1 Kanban Board Structure

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   Backlog   │    Ready    │ In Progress │   Review    │    Done     │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│             │             │             │             │             │
│  Features   │  Refined    │  WIP Limit  │  Testing &  │  Deployed   │
│  & Ideas    │  & Sized    │    = 2      │  Validation │  to Team    │
│             │             │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### 3.2 Work Item Hierarchy

```
Epic (e.g., "Documentation Generation Engine")
  └── Feature (e.g., "Extract Job Metadata")
      └── Story (e.g., "Parse stage definitions from DSX")
          └── Task (e.g., "Implement XML parser for stage nodes")
```

### 3.3 Kanban Principles

1. **Visualize Work:** All work items visible on board
2. **Limit WIP:** Maximum 2 items in progress simultaneously
3. **Manage Flow:** Focus on completing items, not starting new ones
4. **Make Policies Explicit:** Clear definition of "Done" for each column
5. **Feedback Loops:** Weekly reviews with stakeholders
6. **Continuous Improvement:** Retrospective every 2 weeks

### 3.4 Definition of Ready (DoR)

A work item moves to "Ready" when:
- [ ] User story is clearly written with acceptance criteria
- [ ] Technical approach is documented
- [ ] Dependencies are identified
- [ ] Estimated effort is <5 days
- [ ] Test scenarios are defined
- [ ] Required resources/access are available

### 3.5 Definition of Done (DoD)

A work item moves to "Done" when:
- [ ] Code is complete and meets requirements
- [ ] Unit tests written and passing (80%+ coverage)
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Deployed to test environment (or shared with team)
- [ ] Demo completed with stakeholder feedback
- [ ] Accepted by product owner (manager)

---

## 4. Epic & Feature Breakdown

### Epic 1: Foundation - DSX Parser & Metadata Extractor
**Business Value:** Enable automated analysis of DataStage jobs  
**Priority:** P0 (Must Have)  
**Estimated Duration:** 2-3 weeks

#### Features:
1. **F1.1: DSX File Parser**
   - Parse DataStage XML exports
   - Extract job-level metadata (name, description, parameters)
   - Handle multiple DSX format versions
   - **Value:** Foundational capability for all other features
   - **Acceptance:** Successfully parse 10+ real DSX files

2. **F1.2: Stage Metadata Extraction**
   - Identify all stages in a job (source, transformer, target, etc.)
   - Extract stage properties and configurations
   - Parse stage connections (links)
   - **Value:** Understand job structure and flow
   - **Acceptance:** Extract complete metadata from 5+ job types

3. **F1.3: Column-Level Lineage Tracking**
   - Map column transformations across stages
   - Track derivations and calculations
   - Identify source-to-target column mappings
   - **Value:** Critical for data governance and impact analysis
   - **Acceptance:** Correctly trace 90%+ of columns in test jobs

---

### Epic 2: Documentation Generation Engine
**Business Value:** Automated creation of readable documentation  
**Priority:** P0 (Must Have)  
**Estimated Duration:** 2-3 weeks

#### Features:
1. **F2.1: Job Summary Generator**
   - Create executive summary of job purpose
   - Document input sources and output targets
   - List key transformations
   - Generate basic statistics (column count, stage count)
   - **Value:** Quick overview for stakeholders
   - **Acceptance:** Generate summary for any job in <10 seconds

2. **F2.2: Detailed Stage Documentation**
   - Document each stage with purpose and configuration
   - Include transformation logic in readable format
   - Show column mappings and derivations
   - **Value:** Technical reference for developers
   - **Acceptance:** Complete documentation for all stage types

3. **F2.3: Multi-Format Export**
   - Generate Markdown documentation
   - Export to HTML with styling
   - Create PDF reports (optional)
   - **Value:** Flexibility for different use cases
   - **Acceptance:** All 3 formats render correctly

---

### Epic 3: AI-Powered Insights
**Business Value:** Natural language understanding of pipeline logic  
**Priority:** P1 (Should Have)  
**Estimated Duration:** 2-3 weeks

#### Features:
1. **F3.1: Transformation Logic Explainer**
   - Use LLM to explain complex transformation logic
   - Convert SQL/expressions to plain English
   - Generate business-friendly descriptions
   - **Value:** Bridge technical/business understanding gap
   - **Acceptance:** 85%+ stakeholder comprehension in testing

2. **F3.2: Conversational Documentation Interface**
   - Build chatbot that answers questions about pipelines
   - "What does this job do?"
   - "Where does customer_id come from?"
   - "What happens if this stage fails?"
   - **Value:** Self-service documentation access
   - **Acceptance:** Answer 20+ common question types

3. **F3.3: Documentation Quality Checker**
   - Identify missing or incomplete documentation
   - Suggest improvements using AI
   - Flag potentially problematic patterns
   - **Value:** Maintain documentation standards
   - **Acceptance:** Identify gaps in 90%+ of test cases

---

### Epic 4: Advanced Visualization & Analysis
**Business Value:** Visual understanding of complex pipelines  
**Priority:** P2 (Nice to Have)  
**Estimated Duration:** 1-2 weeks

#### Features:
1. **F4.1: Data Flow Diagrams**
   - Generate visual pipeline diagrams
   - Interactive node exploration
   - Export as PNG/SVG
   - **Value:** Quick visual understanding of flows
   - **Acceptance:** Render diagrams for jobs with 20+ stages

2. **F4.2: Dependency Graph Generator**
   - Map job-to-job dependencies
   - Identify upstream/downstream impacts
   - Show table dependencies
   - **Value:** Impact analysis for changes
   - **Acceptance:** Correctly identify dependencies in 90%+ cases

3. **F4.3: Performance Insights**
   - Analyze job configurations for performance issues
   - Identify bottlenecks (e.g., sequential stages that could be parallel)
   - Suggest optimizations
   - **Value:** Proactive performance improvement
   - **Acceptance:** Flag 5+ performance patterns

---

### Epic 5: Integration & Automation
**Business Value:** Seamless workflow integration  
**Priority:** P2 (Nice to Have)  
**Estimated Duration:** 1-2 weeks

#### Features:
1. **F5.1: Batch Processing**
   - Process multiple DSX files at once
   - Generate documentation for entire project
   - Progress tracking and error handling
   - **Value:** Scale to full pipeline inventory
   - **Acceptance:** Process 50+ jobs in single run

2. **F5.2: Change Detection**
   - Compare versions of DSX files
   - Highlight what changed
   - Generate change documentation
   - **Value:** Track pipeline evolution over time
   - **Acceptance:** Detect 95%+ of meaningful changes

3. **F5.3: Documentation Portal**
   - Simple web interface to browse documentation
   - Search across all documented jobs
   - Version history
   - **Value:** Centralized knowledge repository
   - **Acceptance:** Team can find any pipeline doc in <30 seconds

---

## 5. Kanban Board - Initial Backlog

### Backlog (Prioritized Top to Bottom)

#### Week 1-2 Focus
1. ✅ **S1:** Set up project structure and dev environment
2. ✅ **S2:** Research DSX file format and create sample parser
3. 🔄 **S3:** Implement XML parser for job-level metadata
4. 📋 **S4:** Extract stage definitions and types
5. 📋 **S5:** Parse stage links and connections

#### Week 3-4 Focus
6. 📋 **S6:** Extract column metadata from stages
7. 📋 **S7:** Build column lineage tracker
8. 📋 **S8:** Create basic Markdown documentation template
9. 📋 **S9:** Implement job summary generator
10. 📋 **S10:** Generate stage-by-stage documentation

#### Week 5-6 Focus
11. 📋 **S11:** Integrate LLM API (Cohere/OpenAI) for transformation explanations
12. 📋 **S12:** Build prompt engineering for SQL-to-English conversion
13. 📋 **S13:** Create conversational interface prototype
14. 📋 **S14:** Implement RAG system for documentation Q&A
15. 📋 **S15:** Build documentation quality checker

#### Week 7-8 Focus (Stretch)
16. 📋 **S16:** Generate data flow diagrams using Graphviz/D3.js
17. 📋 **S17:** Build dependency graph analyzer
18. 📋 **S18:** Create batch processing CLI
19. 📋 **S19:** Develop simple web portal for docs
20. 📋 **S20:** Implement version comparison

Legend:
- ✅ Done
- 🔄 In Progress
- 📋 Ready/Backlog

---

## 6. User Stories

### Story Format
```
As a [role]
I want to [action]
So that [benefit]

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
```

### Example Stories (Epic 1)

**Story 1.1: Parse DataStage Job Metadata**
```
As a DataStage developer
I want to automatically extract job metadata from DSX files
So that I don't have to manually document basic job information

Acceptance Criteria:
- [ ] Parse job name, description, and version
- [ ] Extract all job parameters with default values
- [ ] Identify job type (server/parallel)
- [ ] Handle corrupted or incomplete DSX files gracefully
- [ ] Process files up to 50MB in size
- [ ] Complete parsing in <5 seconds for typical jobs

Technical Notes:
- Use lxml for XML parsing (faster than ElementTree)
- Implement error handling for malformed XML
- Extract parameters from both job-level and stage-level definitions

Testing:
- Unit tests with 5+ sample DSX files
- Edge case: Empty job, job with special characters in name
- Performance test with large DSX file
```

**Story 1.2: Extract Stage Information**
```
As a data engineer
I want to see all stages in a DataStage job with their types
So that I can quickly understand the job structure

Acceptance Criteria:
- [ ] Identify all stage types (Sequential File, Transformer, ODBC, etc.)
- [ ] Extract stage names and labels
- [ ] Capture stage properties and settings
- [ ] Map stage connections (input/output links)
- [ ] Preserve stage execution order

Technical Notes:
- Create Stage class hierarchy for different stage types
- Parse stage properties from XML attributes
- Build adjacency list for stage connections

Testing:
- Test with job containing 10+ different stage types
- Verify stage order matches DataStage Designer
```

**Story 2.1: Generate Job Summary Document**
```
As a business analyst
I want a high-level summary of what a DataStage job does
So that I can understand data flows without technical details

Acceptance Criteria:
- [ ] Summary includes: job purpose, source systems, target systems
- [ ] List key business entities processed
- [ ] Show frequency/schedule if available
- [ ] Include data volume estimates
- [ ] Generate in under 15 seconds
- [ ] Output in Markdown format

Technical Notes:
- Use template engine (Jinja2) for documentation generation
- Extract business context from job descriptions and stage names
- Include sample output in repository

Testing:
- Generate summaries for 5 different job types
- Validate Markdown syntax
- Peer review for readability
```

**Story 3.1: Explain Transformation Logic**
```
As a product owner
I want plain-English explanations of complex transformations
So that I can validate business logic without reading SQL

Acceptance Criteria:
- [ ] Convert SQL expressions to natural language
- [ ] Explain DataStage built-in functions
- [ ] Handle nested transformations
- [ ] Provide context for derived columns
- [ ] Flag potential data quality issues

Technical Notes:
- Use Cohere/OpenAI API for natural language generation
- Build prompt library for common transformation patterns
- Cache LLM responses to reduce API costs
- Implement retry logic for API failures

Testing:
- Test with 20+ transformation types
- Validate accuracy with domain experts
- Measure API cost per job
```

---

## 7. Technical Architecture

### 7.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  CLI Tool    │  Web Portal  │  Chat Bot    │  API Endpoint  │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘

WIP Limit: 2 | Cycle Time Avg: 2.5 days | Throughput: 2-3/week
```

---

## 16. Appendix B: Story Templates

### Feature Story Template
```markdown
## Story ID: [F#.#] - [Short Title]

**Epic:** [Epic Name]
**Priority:** [P0/P1/P2]
**Estimated Effort:** [S/M/L] ([1-2/3-4/5+ days])
**Assigned To:** Anindita Bornomala

### User Story
As a [role]
I want to [action]
So that [benefit]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Technical Implementation Notes
- Implementation approach
- Key libraries/APIs to use
- Design patterns to follow
- Performance considerations

### Dependencies
- [ ] Dependency 1 (Story ID if applicable)
- [ ] Dependency 2

### Testing Strategy
**Unit Tests:**
- Test case 1
- Test case 2

**Integration Tests:**
- Integration scenario 1

**Edge Cases:**
- Edge case 1
- Edge case 2

### Definition of Done
- [ ] Code complete and committed
- [ ] Unit tests written (80%+ coverage)
- [ ] Integration tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Demo prepared
- [ ] Deployed/shared with team

### Notes & Learnings
[To be filled during/after implementation]
```

---

## 17. Appendix C: Sample Output Documentation

### Example: Generated Job Documentation

```markdown
# DataStage Job Documentation
## Customer_Daily_Load

**Generated:** 2025-10-22 14:30:00  
**Job Version:** 1.2.3  
**Last Modified:** 2025-09-15  
**Generated By:** DataStage Documentation Assistant v1.0

---

## Executive Summary

This DataStage job performs a daily full load of customer data from CSV files 
into the Teradata enterprise data warehouse. The job processes approximately 
50,000 customer records daily, applying data quality checks and transformations 
before loading into the DIM_CUSTOMER dimension table.

**Key Information:**
- **Frequency:** Daily at 2:00 AM EST
- **Average Runtime:** 12 minutes
- **Source System:** CRM Export Files
- **Target System:** Teradata EDW (PROD_EDW)
- **Business Owner:** Customer Analytics Team

---

## Data Flow Overview

```
CSV Files → Data Quality Check → Transform → Teradata
            ↓
        Reject Records
```

**Stage Count:** 5 stages  
**Link Count:** 6 links  
**Column Count:** 18 input → 22 output (4 audit columns added)

---

## Source Systems

### Stage: Customer_CSV_Input
**Type:** Sequential File  
**File Pattern:** `/data/landing/customers/customer_export_YYYYMMDD.csv`

**Columns (12):**
| Column Name | Type | Nullable | Description |
|------------|------|----------|-------------|
| customer_id | Integer | No | Unique customer identifier |
| first_name | Varchar(50) | No | Customer first name |
| last_name | Varchar(50) | No | Customer last name |
| email | Varchar(100) | Yes | Customer email address |
| phone | Varchar(20) | Yes | Primary phone number |
| address_line1 | Varchar(100) | Yes | Street address |
| city | Varchar(50) | Yes | City |
| state | Char(2) | Yes | State code |
| zip_code | Varchar(10) | Yes | Postal code |
| signup_date | Date | No | Account creation date |
| customer_type | Varchar(20) | No | Customer segment |
| status | Varchar(10) | No | Account status (Active/Inactive) |

**File Configuration:**
- Delimiter: Comma (,)
- Header Row: Yes
- Encoding: UTF-8
- Null String: "NULL"

---

## Data Quality Checks

### Stage: DQ_Validate_Customer
**Type:** Transformer  
**Purpose:** Validate data quality and route valid/invalid records

**Validation Rules:**

1. **Email Format Validation**
   - *Rule:* Email must contain "@" and "." 
   - *Action:* Reject if invalid
   - *AI Explanation:* This checks that the email address has a valid format 
     by ensuring it contains both an at-symbol and a period, which are required 
     for standard email addresses.

2. **Phone Number Format**
   - *Rule:* Phone must be 10 digits or empty
   - *Action:* Reject if invalid format
   - *AI Explanation:* The phone number validation ensures that when provided, 
     it contains exactly 10 numeric digits representing a standard US phone 
     number format.

3. **Status Value Check**
   - *Rule:* Status must be 'Active' or 'Inactive'
   - *Action:* Reject if invalid
   - *AI Explanation:* This validation ensures data integrity by only allowing 
     predefined status values, preventing typos or invalid statuses from 
     entering the system.

**Outputs:**
- **Valid_Link:** Records passing all validations → Continue to Transform
- **Reject_Link:** Failed records → Reject file for review

---

## Transformations

### Stage: Transform_Customer_Data
**Type:** Transformer  
**Purpose:** Apply business logic and prepare data for loading

**Transformation Logic:**

#### 1. Name Standardization
```sql
Derivation: TRIM(UPCASE(first_name)) AS first_name
            TRIM(UPCASE(last_name)) AS last_name
```
**AI Explanation:** The customer names are standardized by removing extra 
whitespace and converting to uppercase. This ensures consistent formatting 
across all customer records and makes searching and matching more reliable.

#### 2. Full Name Generation
```sql
Derivation: first_name : ' ' : last_name AS full_name
```
**AI Explanation:** Creates a complete customer name by combining the first 
and last names with a space separator. This derived field is useful for 
reports and displays where the full name is needed.

#### 3. Email Normalization
```sql
Derivation: IF ISNULL(email) THEN 'UNKNOWN@NOEMAIL.COM' 
            ELSE TRIM(DOWNCASE(email))
```
**AI Explanation:** Email addresses are converted to lowercase and trimmed 
for consistency. If no email is provided, a placeholder value is used to 
maintain data completeness while clearly indicating missing information.

#### 4. Customer Segment Enrichment
```sql
Derivation: IF customer_type = 'PREMIUM' THEN 'High Value'
            ELSE IF customer_type = 'STANDARD' THEN 'Regular'
            ELSE 'Basic'
```
**AI Explanation:** Translates internal customer type codes into business-
friendly segment descriptions. Premium customers are flagged as high value, 
helping downstream analytics and reporting systems prioritize these customers.

#### 5. Account Age Calculation
```sql
Derivation: DaysSinceFromTimestamp(signup_date) AS account_age_days
```
**AI Explanation:** Calculates how many days have passed since the customer 
signed up by comparing the signup date to the current date. This metric is 
useful for customer lifecycle analysis and retention reporting.

#### 6. Audit Columns
```sql
Derivation: DSJobStartTimestamp AS load_timestamp
            DSJobInvocationId AS job_run_id
            'CUSTOMER_DAILY_LOAD' AS source_system
            CurrentTimestamp() AS insert_timestamp
```
**AI Explanation:** Adds tracking information to each record including when 
the job ran, which specific job execution loaded the data, and the exact 
time of insertion. This audit trail is critical for troubleshooting data 
issues and understanding data freshness.

---

## Target Systems

### Stage: Load_DIM_Customer
**Type:** Teradata Enterprise  
**Connection:** PROD_EDW_Connection  
**Target Table:** EDW_DIM.DIM_CUSTOMER  
**Write Mode:** Truncate and Load

**Target Columns (16):**
| Column Name | Source | Transformation |
|------------|--------|----------------|
| customer_key | Auto-generated | Identity column |
| customer_id | customer_id | Direct mapping |
| full_name | Derived | first_name + ' ' + last_name |
| first_name | first_name | TRIM(UPCASE()) |
| last_name | last_name | TRIM(UPCASE()) |
| email | email | TRIM(DOWNCASE()) or default |
| phone | phone | Direct mapping |
| address_line1 | address_line1 | Direct mapping |
| city | city | Direct mapping |
| state | state | Direct mapping |
| zip_code | zip_code | Direct mapping |
| signup_date | signup_date | Direct mapping |
| customer_segment | Derived | Customer type translation |
| account_age_days | Derived | Calculated from signup_date |
| status | status | Direct mapping |
| load_timestamp | Derived | Job start timestamp |

**Load Strategy:**
- Method: Truncate target table, then bulk insert
- Error Handling: Transaction rollback on failure
- Performance: Array size = 5000, Buffer = 128MB

---

## Rejected Records

### Stage: Capture_Rejects
**Type:** Sequential File  
**Output Path:** `/data/rejects/customer_load_YYYYMMDD_rejects.csv`

**Reject Reasons Captured:**
- Email validation failure
- Phone format error
- Invalid status value
- Constraint violations

**Reject File Format:**
- All source columns plus:
  - reject_reason (VARCHAR)
  - reject_timestamp (TIMESTAMP)

---

## Job Parameters

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| INPUT_PATH | /data/landing/customers | Source file directory |
| INPUT_FILE | customer_export_${RUN_DATE}.csv | Source filename pattern |
| TARGET_SCHEMA | EDW_DIM | Target schema name |
| TARGET_TABLE | DIM_CUSTOMER | Target table name |
| REJECT_PATH | /data/rejects | Reject file directory |
| RUN_DATE | System Date | Processing date (YYYYMMDD) |

---

## Column Lineage

### Example: full_name
```
Source: Customer_CSV_Input
  ├─ first_name (VARCHAR) 
  │  └─ Transformation: TRIM(UPCASE(first_name))
  ├─ last_name (VARCHAR)
  │  └─ Transformation: TRIM(UPCASE(last_name))
  └─ Derivation: first_name : ' ' : last_name
     └─ Target: DIM_CUSTOMER.full_name (VARCHAR(101))
```

### Example: account_age_days
```
Source: Customer_CSV_Input
  └─ signup_date (DATE)
     └─ Transformation: DaysSinceFromTimestamp(signup_date)
        └─ Target: DIM_CUSTOMER.account_age_days (INTEGER)
```

---

## Dependencies

### Upstream Dependencies
- **Job:** Extract_Customer_CRM
  - Must complete successfully before this job runs
  - Produces the input CSV file

### Downstream Dependencies
- **Job:** Customer_Analytics_Aggregate
  - Consumes DIM_CUSTOMER table
- **Job:** Customer_360_View
  - Joins with DIM_CUSTOMER

### Table Dependencies
- **Reads From:**
  - None (file-based source)
- **Writes To:**
  - EDW_DIM.DIM_CUSTOMER (truncate/load)

---

## Error Handling

**Job-Level Settings:**
- Abort on Sequential File read errors: Yes
- Abort on database write errors: Yes
- Warning limit before abort: 50

**Stage-Level Settings:**
- Data Quality Validator: Route to reject link
- Transformer: Log warnings, continue processing
- Teradata Loader: Rollback transaction on error

---

## Performance Characteristics

**Historical Performance:**
- Average Runtime: 12 minutes
- Average Row Count: 50,000 records
- Peak Runtime: 18 minutes (Dec 2024 - holiday surge)
- Rejection Rate: <0.5% average

**Resource Usage:**
- Estimated Memory: 512 MB
- Disk I/O: Moderate
- Network: Low (local file system)

---

## Monitoring & Alerts

**Success Criteria:**
- Job completes within 20 minutes
- Rejection rate < 2%
- Target row count matches source ± 1%

**Alert Conditions:**
- Job failure: Page on-call team
- Runtime > 20 minutes: Warning notification
- Rejection rate > 5%: Email data quality team
- Zero records loaded: Critical alert

---

## Change History

| Date | Version | Change Description | Changed By |
|------|---------|-------------------|------------|
| 2025-09-15 | 1.2.3 | Added account_age_days calculation | J. Smith |
| 2025-06-10 | 1.2.0 | Changed load strategy to truncate/load | M. Johnson |
| 2025-03-01 | 1.1.0 | Added email validation rule | J. Smith |
| 2024-12-15 | 1.0.0 | Initial production deployment | Team Lead |

---

## Questions?

**For Technical Issues:** datastage-support@company.com  
**For Business Logic:** customer-analytics@company.com  
**Job Owner:** Data Engineering Team

---

*This documentation was automatically generated by DataStage Documentation 
Assistant. Last updated: 2025-10-22 14:30:00*
```

---

## 18. Appendix D: LLM Prompt Library

### Prompt 1: Explain Transformation Logic

```yaml
prompt_name: explain_transformation
model: command-r-plus
temperature: 0.3
max_tokens: 300

system_prompt: |
  You are a technical writer specializing in data engineering. Your job is to 
  explain DataStage transformation logic in clear, business-friendly language. 
  Assume your audience includes business analysts who understand data concepts 
  but may not be SQL experts.

user_prompt_template: |
  Explain the following DataStage transformation in plain English:
  
  Column Name: {column_name}
  Data Type: {data_type}
  Derivation: {derivation_expression}
  Source Columns: {source_columns}
  
  Context: This transformation is part of a {job_type} job that processes 
  {entity_type} data.
  
  Provide a 2-3 sentence explanation that:
  1. Describes what the transformation does
  2. Explains why it's useful or important
  3. Uses business-friendly language without technical jargon
  
  Do not include code or technical implementation details.

example_input:
  column_name: "full_name"
  data_type: "VARCHAR(101)"
  derivation_expression: "TRIM(first_name) : ' ' : TRIM(last_name)"
  source_columns: ["first_name", "last_name"]
  job_type: "customer dimension load"
  entity_type: "customer"

example_output: |
  Creates a complete customer name by combining the first and last names with 
  a space in between, after removing any extra whitespace. This derived field 
  provides a ready-to-use full name for reports and customer-facing displays, 
  eliminating the need for applications to concatenate names themselves.
```

### Prompt 2: Generate Job Summary

```yaml
prompt_name: generate_job_summary
model: command-r-plus
temperature: 0.4
max_tokens: 500

system_prompt: |
  You are a data engineering documentation specialist. Create concise, 
  informative summaries of ETL jobs that help stakeholders quickly understand 
  what a pipeline does and why it matters.

user_prompt_template: |
  Generate an executive summary for this DataStage job:
  
  Job Name: {job_name}
  Stage Count: {stage_count}
  Source Systems: {source_list}
  Target Systems: {target_list}
  Key Transformations: {transformation_summary}
  
  Create a 3-4 sentence summary that includes:
  1. The primary purpose of this job
  2. Where data comes from and where it goes
  3. Key business value or use case
  
  Write for a business audience. Focus on business value, not technical details.

example_output: |
  This DataStage job performs a daily full load of customer data from CRM 
  export files into the enterprise data warehouse. The job processes customer 
  demographics, contact information, and account details, applying data quality 
  checks and standardization before loading into the DIM_CUSTOMER dimension 
  table. This pipeline supports customer analytics, segmentation analysis, and 
  enables the organization's 360-degree customer view.
```

### Prompt 3: Identify Data Quality Issues

```yaml
prompt_name: identify_dq_issues
model: command-r-plus
temperature: 0.2
max_tokens: 400

system_prompt: |
  You are a data quality expert reviewing DataStage transformation logic. 
  Identify potential data quality issues, edge cases, and recommend improvements.

user_prompt_template: |
  Review this transformation for potential data quality issues:
  
  Transformation: {transformation_logic}
  Source Columns: {source_columns}
  Target Column: {target_column}
  Nullable: {is_nullable}
  
  Identify:
  1. Potential null handling issues
  2. Data type conversion risks
  3. Edge cases not handled
  4. Recommended improvements
  
  Format as bullet points. Be specific and actionable.

example_output: |
  Potential Issues:
  - If first_name or last_name is null, concatenation will produce unexpected 
    results (e.g., "null John" or "Jane null")
  - No handling for names with special characters (apostrophes, hyphens)
  - Multiple consecutive spaces between names not addressed
  
  Recommendations:
  - Add null checks: IF ISNULL(first_name) OR ISNULL(last_name) THEN 'UNKNOWN'
  - Consider TRIM() to handle multiple spaces
  - Document expected behavior for edge cases in job notes
```

### Prompt 4: Conversational Q&A

```yaml
prompt_name: answer_pipeline_question
model: command-r-plus
temperature: 0.3
max_tokens: 300

system_prompt: |
  You are a helpful assistant that answers questions about DataStage pipelines. 
  Use the provided documentation context to give accurate, specific answers. 
  If you don't know, say so clearly.

user_prompt_template: |
  Context from pipeline documentation:
  {retrieved_context}
  
  Question: {user_question}
  
  Provide a clear, concise answer based on the documentation. If the answer 
  isn't in the provided context, say "I don't have that information in the 
  documentation" and suggest where to find it.

rag_config:
  retriever: "semantic_search"
  top_k: 3
  similarity_threshold: 0.7
```

---

## 19. Appendix E: Testing Checklist

### Unit Testing Checklist

#### DSX Parser Module
- [ ] Parse job with all standard stage types
- [ ] Handle malformed XML gracefully
- [ ] Extract parameters correctly
- [ ] Parse stage properties with special characters
- [ ] Handle empty/minimal DSX file
- [ ] Parse very large DSX file (>10MB)
- [ ] Extract column metadata with all data types
- [ ] Handle missing/optional XML elements

#### Transformation Explainer
- [ ] Explain simple derivation (concatenation)
- [ ] Explain complex SQL expression
- [ ] Handle nested transformations
- [ ] Explain DataStage built-in functions
- [ ] Generate explanation for null handling logic
- [ ] Explain aggregation logic
- [ ] Handle transformation with 10+ operations

#### Documentation Generator
- [ ] Generate Markdown from complete job
- [ ] Generate HTML with proper styling
- [ ] Handle job with no transformations
- [ ] Handle job with 20+ stages
- [ ] Generate lineage for derived columns
- [ ] Create documentation for rejected records handling
- [ ] Export with special characters in names

### Integration Testing Checklist

#### End-to-End Workflows
- [ ] Parse DSX → Generate Markdown → Validate output
- [ ] Parse DSX → Explain transformations → Include in docs
- [ ] Parse multiple jobs → Batch generate docs
- [ ] CLI: Generate docs from config file
- [ ] CLI: Interactive mode complete workflow
- [ ] API: Submit job → Receive documentation
- [ ] Chatbot: Ask question → Retrieve answer

#### Performance Testing
- [ ] Parse 50 DSX files in <5 minutes
- [ ] Generate documentation for complex job in <30 seconds
- [ ] LLM API calls complete in <10 seconds
- [ ] Batch process 100 jobs without memory issues

### User Acceptance Testing Checklist

#### Usability
- [ ] Non-technical user can generate documentation
- [ ] Error messages are clear and actionable
- [ ] Documentation is readable by business stakeholders
- [ ] 85%+ accuracy on transformation explanations (validated by SMEs)
- [ ] Team can find information in <30 seconds
- [ ] CLI commands are intuitive

#### Functional
- [ ] All sample jobs generate valid documentation
- [ ] Chatbot answers 20+ common question types
- [ ] Lineage diagrams are accurate
- [ ] Generated docs match manual documentation (spot check)

---

## 20. Appendix F: GitHub Copilot Usage Guide

### Recommended Copilot Practices for This Project

#### 1. Context-Aware Development
```python
# Give Copilot context by creating clear file headers
"""
Module: dsx_parser.py
Purpose: Parse DataStage DSX (XML) files and extract job metadata

This module handles:
- XML parsing of DSX exports
- Extraction of job-level metadata (name, description, parameters)
- Stage definition parsing
- Link and connection mapping

Dependencies: lxml, dataclasses
"""

# Now Copilot will generate more relevant suggestions
```

#### 2. Use Copilot Chat for Architecture
```
You: /explain how should I structure a class to represent a DataStage job 
with stages, links, and parameters?

Copilot: [Provides dataclass structure]

You: Generate a complete dataclass for DataStageJob with methods for 
lineage tracking and documentation generation
```

#### 3. Leverage Copilot for Tests
```python
def test_parse_job_metadata():
    """Test that job-level metadata is correctly extracted from DSX"""
    # Copilot will suggest:
    # - Setup code
    # - Sample data
    # - Assertions
    # - Edge cases
```

Use `/tests` command in Copilot Chat to generate comprehensive test suites.

#### 4. Prompt Engineering Help
```
You: I need to write a prompt for an LLM to explain DataStage transformation 
logic in business-friendly language. The prompt should:
- Take a derivation expression as input
- Output 2-3 sentences
- Avoid technical jargon
- Explain business value

Help me structure this prompt with examples.
```

#### 5. Documentation Generation
Use `/doc` command to generate docstrings:
```python
def extract_column_lineage(self, target_column: str) -> List[Column]:
    # Write implementation
    # Then use: /doc to generate docstring
    pass
```

#### 6. Code Review with Copilot
Before committing:
```
You: Review this function for potential issues, edge cases, and improvements:
[paste code]

Copilot: [Provides feedback on error handling, edge cases, performance]
```

#### 7. Refactoring Assistant
```
You: This function is too long. Help me refactor it into smaller, more 
maintainable functions.

Copilot: [Suggests decomposition strategy]
```

### Copilot Limitations to Watch For

1. **DataStage-Specific Knowledge**: Copilot may not know all DataStage stage 
   types or DSX format specifics. Validate suggestions against actual DSX files.

2. **LLM API Patterns**: Copilot might suggest outdated API patterns. Check 
   Cohere/OpenAI docs for current best practices.

3. **Over-Complexity**: Copilot sometimes suggests overly complex solutions. 
   Keep it simple, especially for MVP.

4. **Testing Real Files**: Copilot can't test with your actual DSX files. 
   Always validate generated code with real data.

---

## 21. Project Kickoff Agenda

### Week 1 - Day 1 Kickoff Meeting (60 minutes)

**Attendees:** Anindita + Manager + Optional: DataStage SME

#### Agenda

**1. Project Overview (10 min)**
- Why this project matters
- Expected outcomes and value
- How it fits into program goals

**2. Requirements Walkthrough (15 min)**
- Review requirements document
- Clarify scope and priorities
- Discuss Kanban approach
- Q&A on unclear items

**3. Technical Setup (15 min)**
- Review technology stack
- Confirm GitHub Copilot access
- Discuss development environment
- Access to sample DSX files
- LLM API access (Cohere/OpenAI keys)

**4. Kanban Board Setup (10 min)**
- Choose board tool (GitHub Projects, Trello, Jira)
- Walk through board columns
- Create first 5 stories together
- Explain WIP limits

**5. Working Agreement (5 min)**
- Weekly sync schedule
- Communication preferences (Slack/Email)
- When to ask for help
- Code review process

**6. First Week Plan (5 min)**
- Assign first 2 stories
- Set goals for Week 1
- Schedule next check-in

**Action Items:**
- [ ] Anindita: Set up development environment
- [ ] Manager: Provide 5+ sample DSX files
- [ ] Anindita: Create Kanban board and add initial stories
- [ ] Manager: Set up LLM API access
- [ ] Both: Schedule weekly recurring meeting

---

## 22. Success Metrics Dashboard

Track progress weekly with these metrics:

```
┌────────────────────────────────────────────────────────┐
│   DataStage Documentation Assistant - Week 3 Metrics   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  📊 Flow Metrics                                       │
│    Stories Completed: 8 / 20 (40%)                     │
│    Cycle Time Avg: 2.5 days ✅ (Target: <3)            │
│    Throughput: 2.7 stories/week ✅                     │
│    WIP: 2 / 2 (at limit)                               │
│                                                        │
│  ✅ Quality Metrics                                    │
│    Test Coverage: 82% ✅ (Target: >80%)                │
│    Code Review Pass Rate: 100%                         │
│    Bugs Found: 1 (low severity)                        │
│                                                        │
│  💰 Value Metrics                                      │
│    Documentation Time: 45 min ⚠️  (Target: <30)        │
│    Team Usage: N/A (not deployed yet)                  │
│    Jobs Documented: 12                                 │
│                                                        │
│  🎯 Project Health                                     │
│    On Track for MVP: ✅ Yes                            │
│    Blockers: 0                                         │
│    Days to MVP: 8                                      │
│                                                        │
└────────────────────────────────────────────────────────┘

Legend: ✅ On Target | ⚠️  Needs Attention | ❌ At Risk
```

---

## 23. Frequently Asked Questions

**Q: What if I get stuck on a story for more than 2 days?**
A: Mark it as blocked, move it back to "Ready," and pull a different story. 
Discuss the blocker in your next weekly sync.

**Q: Can I work on 3 stories at once if they're small?**
A: No. WIP limit is 2. Finish what you start before pulling more work. This 
prevents context-switching and ensures faster delivery.

**Q: What if stakeholders request new features mid-project?**
A: Add them to the backlog. Prioritize in the weekly sync. Don't start new 
work until current WIP is complete.

**Q: How do I handle LLM API costs?**
A: Implement caching aggressively. Track costs weekly. If exceeding budget, 
discuss alternative approaches (smaller model, fewer calls, batch processing).

**Q: What if the DSX format is more complex than expected?**
A: Start with the simplest jobs. Document complexity. Adjust estimates. It's 
okay to descope advanced features to maintain MVP timeline.

**Q: Should I build unit tests as I go or at the end?**
A: As you go. Tests are part of the Definition of Done for each story. They 
help you code faster and catch issues early.

**Q: When should I ask for help?**
A: Immediately when:
- Blocked for >4 hours on a technical issue
- Unsure about requirements interpretation  
- Need access to resources
- Estimates are way off

**Q: Can I use GitHub Copilot for everything?**
A: Use it extensively, but:
- Review all generated code carefully
- Validate with actual DSX files
- Don't blindly accept suggestions
- Learn from the patterns it shows you

---

## 24. Resources & References

### Documentation
- **IBM DataStage Documentation**: [IBM Knowledge Center]
- **Python lxml**: https://lxml.de/
- **Cohere API Docs**: https://docs.cohere.com/
- **GitHub Copilot Best Practices**: [GitHub Docs]

### Sample Code Repositories
- [To be added: Similar open-source projects if available]

### Internal Resources
- Team Confluence/Wiki
- DataStage best practices guide
- Sample DSX files repository
- LLM prompt library

### Support Contacts
- **Manager**: [Name/Email] - Weekly syncs, prioritization, blockers
- **DataStage SME**: [Name/Email] - Technical DataStage questions
- **DevOps**: [Name/Email] - Environment/access issues

---

## 25. Final Checklist - Project Completion

### Code Deliverables
- [ ] GitHub repository with clean, documented code
- [ ] All tests passing (>80% coverage)
- [ ] No critical bugs or blockers
- [ ] README with quickstart guide
- [ ] requirements.txt and setup instructions

### Documentation Deliverables
- [ ] User manual
- [ ] API reference (if applicable)
- [ ] Architecture documentation
- [ ] Troubleshooting guide
- [ ] Sample outputs

### Deployment Deliverables
- [ ] CLI tool accessible to team
- [ ] Sample DSX files processed successfully
- [ ] Demo environment set up
- [ ] Access instructions provided

### Knowledge Transfer
- [ ] 1-hour team training completed
- [ ] Video walkthrough recorded
- [ ] Handover document prepared
- [ ] Future enhancements backlog documented
- [ ] Retrospective completed

### Metrics & Validation
- [ ] Success criteria met (see Section 13)
- [ ] Stakeholder acceptance received
- [ ] Usage metrics collected
- [ ] Time savings validated

---

**Document Owner:** [Manager Name]  
**Prepared For:** Anindita Bornomala  
**Last Updated:** October 22, 2025  
**Next Review:** Weekly during project execution

---

*This requirements document is a living artifact. Update as needed based on 
learnings and changing priorities. The Kanban approach allows flexibility—
embrace change while maintaining focus on delivering value.*─┴────────────────┘
                            │
       ┌────────────────────┴────────────────────┐
       │        Core Documentation Engine        │
       ├─────────────────────────────────────────┤
       │  - Job Analyzer                         │
       │  - Metadata Extractor                   │
       │  - Lineage Tracker                      │
       │  - Documentation Generator              │
       └────────────┬────────────────────────────┘
                    │
       ┌────────────┴────────────┬────────────────┐
       │                         │                │
┌──────┴───────┐      ┌──────────┴───────┐  ┌─────┴────────┐
│ DSX Parser   │      │   AI Services    │  │  Renderers   │
├──────────────┤      ├──────────────────┤  ├──────────────┤
│ - XML Reader │      │ - LLM Integration│  │ - Markdown   │
│ - Validator  │      │ - Prompt Manager │  │ - HTML       │
│ - Schema Map │      │ - RAG System     │  │ - PDF        │
└──────────────┘      └──────────────────┘  └──────────────┘
       │                         │                │
       └─────────────────────────┴────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │   Storage Layer   │
                  ├───────────────────┤
                  │ - File System     │
                  │ - Vector DB       │
                  │ - Cache (Redis)   │
                  └───────────────────┘
```

### 7.2 Technology Stack

**Core Technologies:**
- **Language:** Python 3.9+
- **XML Parsing:** lxml (high performance)
- **Documentation:** Jinja2 templates, markdown
- **AI/ML:** 
  - LLM: Cohere API (primary) or OpenAI
  - Vector DB: ChromaDB or FAISS (for RAG)
  - Embeddings: sentence-transformers
- **Visualization:** Graphviz, D3.js (for diagrams)
- **Web Framework:** FastAPI (for API/portal)
- **CLI:** Click
- **Testing:** pytest, pytest-mock

**Development Tools:**
- **GitHub Copilot:** Code generation and documentation
- **Pre-commit hooks:** black, pylint, mypy
- **CI/CD:** GitHub Actions (optional)

### 7.3 Project Structure

```
datastage-doc-assistant/
├── README.md
├── KANBAN_BOARD.md            # Track work items
├── requirements.txt
├── setup.py
├── .env.example               # API keys template
├── config/
│   ├── prompts.yaml           # LLM prompt templates
│   └── doc_templates.yaml     # Documentation templates
├── src/
│   └── doc_assistant/
│       ├── __init__.py
│       ├── cli.py             # CLI entry point
│       ├── core/
│       │   ├── parser.py      # DSX XML parser
│       │   ├── analyzer.py    # Job analysis logic
│       │   ├── lineage.py     # Column lineage tracker
│       │   └── generator.py   # Documentation generator
│       ├── ai/
│       │   ├── llm_client.py  # LLM API wrapper
│       │   ├── prompts.py     # Prompt engineering
│       │   ├── explainer.py   # Transformation explainer
│       │   └── rag.py         # RAG system for chatbot
│       ├── renderers/
│       │   ├── markdown.py
│       │   ├── html.py
│       │   └── diagrams.py
│       ├── models/
│       │   ├── job.py         # Job data model
│       │   ├── stage.py       # Stage data model
│       │   └── column.py      # Column data model
│       ├── utils/
│       │   ├── cache.py
│       │   └── validators.py
│       └── api/               # FastAPI application
│           ├── main.py
│           ├── routes.py
│           └── templates/     # HTML templates
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│       ├── sample_dsx/        # Sample DSX files
│       └── expected_output/   # Expected documentation
├── docs/
│   ├── setup.md
│   ├── usage.md
│   ├── architecture.md
│   └── api_reference.md
└── examples/
    ├── basic_usage.py
    └── sample_output/         # Generated documentation samples
```

### 7.4 Data Models

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class StageType(Enum):
    SEQUENTIAL_FILE = "CSeqFile"
    TRANSFORMER = "PxTransformer"
    ODBC = "CODBCSTAGE"
    TERADATA = "PxTeradata"
    AGGREGATOR = "PxAggregator"
    # ... more types

@dataclass
class Column:
    name: str
    data_type: str
    length: Optional[int]
    nullable: bool
    description: Optional[str]
    source_columns: List[str]  # For lineage
    transformation: Optional[str]

@dataclass
class Link:
    from_stage: str
    to_stage: str
    link_type: str  # primary, reference, reject
    columns: List[Column]

@dataclass
class Stage:
    name: str
    stage_type: StageType
    properties: Dict[str, any]
    input_columns: List[Column]
    output_columns: List[Column]
    transformation_logic: Optional[str]
    
    def get_ai_description(self) -> str:
        """Generate natural language description using LLM"""
        pass

@dataclass
class DataStageJob:
    name: str
    description: str
    parameters: Dict[str, any]
    stages: List[Stage]
    links: List[Link]
    created_date: str
    version: str
    
    def generate_summary(self) -> str:
        """Generate executive summary"""
        pass
    
    def get_lineage(self, column_name: str) -> List[Column]:
        """Trace column lineage"""
        pass
    
    def to_markdown(self) -> str:
        """Export to Markdown documentation"""
        pass
```

---

## 8. Kanban Ceremonies & Rituals

### 8.1 Daily Stand-up (Async)
**Frequency:** Daily (posted in Slack/Teams by 10 AM)  
**Duration:** Written update, <5 min to read  
**Format:**
```
Yesterday: Completed Story 1.1 - DSX parser working for job metadata
Today: Working on Story 1.2 - Stage extraction
Blockers: Need sample DSX file with ODBC stages for testing
```

### 8.2 Weekly Sync
**Frequency:** Once per week  
**Duration:** 30 minutes  
**Participants:** Anindita + Manager  
**Agenda:**
1. Demo completed work items (10 min)
2. Review board and pull next items (5 min)
3. Discuss blockers and technical questions (10 min)
4. Feedback and adjust priorities (5 min)

### 8.3 Bi-weekly Retrospective
**Frequency:** Every 2 weeks  
**Duration:** 30 minutes  
**Format:** Start/Stop/Continue
- What should we start doing?
- What should we stop doing?
- What should we continue doing?

### 8.4 Ad-hoc Stakeholder Demos
**Frequency:** As features complete  
**Duration:** 15 minutes  
**Purpose:** Get feedback early, validate direction

---

## 9. Metrics & KPIs

### 9.1 Flow Metrics

**Cycle Time:** Time from "In Progress" to "Done"
- **Target:** <3 days per story
- **Measure:** Track in Kanban board

**Throughput:** Stories completed per week
- **Target:** 2-3 stories/week
- **Measure:** Weekly completion count

**Work in Progress (WIP):** Active stories
- **Limit:** Maximum 2 stories in progress
- **Measure:** Count items in "In Progress" column

### 9.2 Quality Metrics

**Test Coverage:** Unit test coverage
- **Target:** >80% coverage
- **Measure:** pytest-cov reports

**Documentation Accuracy:** AI explanation correctness
- **Target:** >85% stakeholder validation
- **Measure:** Survey after demos

**Bug Escape Rate:** Bugs found after "Done"
- **Target:** <10% of stories
- **Measure:** Track reopened items

### 9.3 Value Metrics

**Time Saved:** Documentation time reduction
- **Baseline:** 4-6 hours manual documentation per job
- **Target:** <30 minutes with tool
- **Measure:** Time tracking before/after

**Adoption Rate:** Team usage
- **Target:** 80% of team using tool by week 8
- **Measure:** Usage logs, surveys

---

## 10. Risk Management

| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|-------------|------------|-------|
| DSX format complexity exceeds estimates | High | Medium | Start with simplest jobs; iterate; budget extra time for Epic 1 | Anindita |
| LLM API costs exceed budget | Medium | Low | Implement aggressive caching; use batch processing; monitor costs weekly | Manager |
| Scope creep from stakeholders | Medium | High | Strictly enforce WIP limits; park new ideas in backlog; prioritize in weekly sync | Manager |
| Limited DSX file samples | High | Medium | Request diverse sample files in week 1; create synthetic examples if needed | Manager |
| Integration with existing tools delayed | Low | Low | Design for standalone use first; integration as separate epic | Anindita |

---

## 11. Weekly Execution Plan

### Week 1: Foundation Sprint
**Goal:** Get first value delivered - basic DSX parsing

**Monday-Tuesday:**
- Set up project structure
- Research DSX format
- Create project board in GitHub Projects or Trello

**Wednesday-Thursday:**
- Story 1.1: Parse job-level metadata
- Write unit tests
- Demo to manager

**Friday:**
- Story 1.2: Extract stage definitions (start)
- Weekly sync
- Update board

**Deliverable:** Tool that extracts and prints job metadata

---

### Week 2: Metadata Extraction
**Goal:** Complete Epic 1 foundation

**Monday-Tuesday:**
- Story 1.2: Complete stage extraction
- Story 1.3: Parse stage links

**Wednesday-Thursday:**
- Story 1.4: Column metadata extraction (start)
- Add integration tests

**Friday:**
- Story 1.4: Complete column extraction
- Weekly sync and demo
- Retrospective

**Deliverable:** Complete job structure parser

---

### Week 3: Basic Documentation
**Goal:** First documentation output

**Monday-Tuesday:**
- Story 2.1: Job summary generator
- Create Markdown templates

**Wednesday-Thursday:**
- Story 2.2: Stage documentation generator
- Test with 5+ real jobs

**Friday:**
- Story 2.3: Multi-format export (Markdown + HTML)
- Weekly sync
- Stakeholder demo

**Deliverable:** Automated documentation generation

---

### Week 4: AI Integration Begins
**Goal:** Add intelligence to documentation

**Monday-Tuesday:**
- Story 3.1: Integrate LLM API
- Build prompt templates
- Test transformation explanations

**Wednesday-Thursday:**
- Story 3.1: Refine prompts based on testing
- Add error handling and retries

**Friday:**
- Demo AI explanations
- Weekly sync and retrospective

**Deliverable:** AI-powered transformation explanations

---

### Week 5-6: Conversational Interface
**Goal:** Interactive documentation access

**Focus:** Stories 3.2 (Chatbot) and 3.3 (Quality Checker)

**Deliverable:** Chatbot that answers pipeline questions

---

### Week 7-8: Polish & Advanced Features
**Goal:** Visualization and deployment

**Focus:** Epic 4 features based on priorities

**Deliverable:** Production-ready tool with visualizations

---

## 12. Stakeholder Communication Plan

### Weekly Updates (Email/Slack)
**To:** Manager + interested team members  
**Content:**
- Completed work items with screenshots
- Upcoming focus for next week
- Any blockers or requests for input

**Template:**
```
DataStage Doc Assistant - Week [X] Update

✅ Completed This Week:
- Story 1.1: DSX parser now extracts job metadata (demo: [link])
- Story 1.2: Stage extraction complete - handles 8 stage types

🔄 In Progress:
- Story 1.3: Building column lineage tracker

📋 Next Week Focus:
- Complete Epic 1 (Metadata Extraction)
- Start Epic 2 (Documentation Generation)

🚧 Blockers:
- Need sample DSX files with Aggregator stages for testing

📊 Metrics:
- Cycle time: 2.5 days (target: <3)
- Test coverage: 82%
- Stories completed: 2
```

### Monthly Demos
**To:** Broader team + stakeholders  
**Duration:** 30 minutes  
**Content:**
- Live demo of new capabilities
- Sample output walkthrough
- Gather feedback and feature requests

---

## 13. Success Criteria

### Minimum Viable Product (MVP)
Deliver by Week 4:
- [ ] Parse any DSX file and extract metadata
- [ ] Generate Markdown documentation automatically
- [ ] Include AI-powered transformation explanations
- [ ] CLI tool for single job documentation
- [ ] Process 10+ real DataStage jobs successfully

### Full Success
Deliver by Week 8:
- [ ] All MVP features plus:
- [ ] Conversational chatbot interface
- [ ] Batch processing for multiple jobs
- [ ] HTML output with styling
- [ ] Data flow diagrams
- [ ] 80%+ team adoption
- [ ] >80% time savings validated
- [ ] Documentation for 50+ pipelines generated

### Stretch Goals
- [ ] Web portal for browsing documentation
- [ ] Version comparison and change tracking
- [ ] Integration with Confluence/SharePoint
- [ ] Automated documentation updates via CI/CD
- [ ] Performance optimization insights

---

## 14. Handover & Knowledge Transfer

### Deliverables at Project End

**Code & Documentation:**
- [ ] GitHub repository with complete code
- [ ] Comprehensive README
- [ ] API documentation
- [ ] Architecture decision records (ADRs)

**Operational:**
- [ ] Deployment guide
- [ ] User manual
- [ ] Troubleshooting guide
- [ ] Prompt library for LLM

**Training:**
- [ ] 1-hour training session for team
- [ ] Video walkthrough (15-20 min)
- [ ] FAQ document

**Transition:**
- [ ] Handover to designated team member for maintenance
- [ ] Backlog of future enhancements
- [ ] Lessons learned document

---

## 15. Appendix A: Sample Kanban Board Layout

```
┌──────────────────────────────────────────────────────────────┐
│                   DataStage Doc Assistant                    │
│                     Kanban Board - Week 3                    │
├──────────────┬─────────────┬─────────────┬─────────────┬─────┤
│   Backlog    │    Ready    │In Progress  │   Review    │ Done│
│   (20)       │    (5)      │   (2/2)     │    (1)      │ (8) │
├──────────────┼─────────────┼─────────────┼─────────────┼─────┤
│              │             │             │             │     │
│ S11: LLM     │ S6: Column  │ S4: Stage   │ S3: Job     │ S1  │
│   Integration│   Metadata  │   Extract   │   Parser    │ S2  │
│              │             │   [Day 2/3] │   [Testing] │     │
│ S12: Prompt  │ S7: Lineage │ ──────────  │             │     │
│   Engineering│   Tracker   │ S5: Links   │             │     │
│              │             │   [Day 1/2] │             │     │
│ S13: Chatbot │ S8: MD      │             │             │     │
│              │   Template  │             │             │     │
│ S14: RAG     │             │             │             │     │
│              │ S9: Summary │             │             │     │
│ ...          │   Generator │             │             │     │
│              │             │             │             │     │
└──────────────┴───────────────────────────────────────────────