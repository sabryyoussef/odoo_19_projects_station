# CRM Lead Audit Automation System - Implementation Plan

## Project Overview
**Objective:** Automate the auditing of CRM Leads that remain in "New" stage for more than 48 hours without scheduled activities.

**Target Odoo Version:** 16+ (Compatible with Odoo 19)

---

## Phase 1: Strategic Planning

### 1.1 Schema Modifications

#### Model: `crm.lead`
**Technical Field Names to be Added:**

| Field Name | Type | Description | Required | Default |
|------------|------|-------------|----------|---------|
| `x_is_audited` | Boolean | Flag indicating if the lead has been audited | Yes | False |
| `x_last_audit_date` | Datetime | Timestamp of the last audit performed | No | None |

**Rationale:**
- Using `x_` prefix for custom fields to avoid conflicts with standard Odoo fields
- Boolean field for quick filtering and status tracking
- Datetime field for audit history and reporting purposes

### 1.2 Workflow Logic

#### Filtering Criteria for "Stale" Leads:

```python
FILTER_CRITERIA = {
    'type': 'lead',                    # Only leads, not opportunities
    'probability': '<100',             # Not won (100% probability)
    'x_is_audited': False,            # Not yet audited
    'create_date': '< 48 hours ago',  # Created more than 48 hours ago
    'activity_ids': [],               # No scheduled activities
}
```

#### Business Rules:
1. **Trigger Condition:** Lead exists > 48 hours with no activities
2. **Action:** Create a "To Do" activity for the assigned salesperson
3. **Audit Marking:** Set `x_is_audited = True` after activity creation
4. **Audit Reset Logic:** Consider resetting `x_is_audited` when:
   - Lead stage changes
   - New activity is manually created
   - Lead is converted to opportunity

### 1.3 Security & Credentials Management

#### Recommended Approach: Environment Variables

**Environment Variables Required:**
```bash
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=automation_user@company.com
ODOO_PASSWORD=secure_password_here
ODOO_PORT=8069  # Optional, default 8069
```

**Security Best Practices:**
1. **Development:** Use `.env` file with `python-dotenv` library
2. **Production:** Use system environment variables or secret management tools:
   - **Azure Key Vault** (Microsoft Azure)
   - **AWS Secrets Manager** (Amazon Web Services)
   - **HashiCorp Vault** (On-premise)
   - **Kubernetes Secrets** (Container environments)

3. **User Permissions:**
   - Create a dedicated technical user for automation
   - Assign minimal required permissions:
     - Read access on `crm.lead`
     - Create access on `mail.activity`
     - Write access on `crm.lead` (for audit flags)

### 1.4 Integration Architecture

#### Communication Flow:

```
┌─────────────────────┐
│  Cron Job/Scheduler │
│   (Daily @ 08:00)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python Script      │
│  (automation.py)    │
└──────────┬──────────┘
           │
           │ erppeek.Client()
           ▼
┌─────────────────────┐
│  Odoo XML-RPC API   │
│  (Port 8069/8443)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Odoo ORM           │
│  - crm.lead         │
│  - mail.activity    │
└─────────────────────┘
```

#### erppeek Connection Method:
```python
import erppeek

# Connect to Odoo
client = erppeek.Client(
    server=os.getenv('ODOO_URL'),
    db=os.getenv('ODOO_DB'),
    user=os.getenv('ODOO_USERNAME'),
    password=os.getenv('ODOO_PASSWORD')
)

# Access models
Lead = client.model('crm.lead')
Activity = client.model('mail.activity')
```

#### Error Handling Strategy:
1. **Connection Failures:** Retry logic with exponential backoff
2. **Authentication Errors:** Log and alert system administrators
3. **Query Failures:** Transaction rollback and detailed logging
4. **Partial Success:** Continue processing remaining leads

---

## Phase 2: Odoo Module Structure

### Module Name: `crm_lead_audit`

### File Structure:
```
crm_lead_audit/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── crm_lead.py
├── views/
│   └── crm_lead_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

### Dependencies:
- `crm` (base CRM module)
- `mail` (for activity management)

---

## Phase 3: Automation Script Specifications

### Script Name: `lead_audit_automation.py`

### Key Functions:
1. `connect_to_odoo()` - Establish erppeek connection
2. `fetch_stale_leads()` - Query leads matching criteria
3. `create_audit_activity(lead_id, user_id)` - Create activity
4. `mark_lead_audited(lead_id)` - Update audit flag
5. `main()` - Orchestrate the automation workflow

### Logging Requirements:
- Log file: `lead_audit_{date}.log`
- Log level: INFO (configurable)
- Log format: `[TIMESTAMP] [LEVEL] [MESSAGE]`

### Performance Considerations:
- Batch processing for large datasets
- Limit query results (e.g., max 500 leads per run)
- Implement timeout mechanisms

---

## Phase 4: Deployment Options

### Option A: Linux Crontab
```bash
0 8 * * * /usr/bin/python3 /path/to/lead_audit_automation.py >> /var/log/odoo_automation.log 2>&1
```

### Option B: Windows Task Scheduler
- Trigger: Daily at 08:00 AM
- Action: Start a program
- Program: `python.exe`
- Arguments: `lead_audit_automation.py`

### Option C: Jenkins Pipeline
```groovy
pipeline {
    triggers {
        cron('0 8 * * *')  // Daily at 08:00 AM
    }
    stages {
        stage('Run Lead Audit') {
            steps {
                sh 'python3 lead_audit_automation.py'
            }
        }
    }
}
```

### Option D: Odoo Native Scheduled Action
- Create `ir.cron` record in Odoo
- Advantage: No external scheduler needed
- Limitation: Requires script to be within Odoo module

---

## Risk Assessment & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Script failure during execution | High | Implement comprehensive error handling and alerting |
| Performance degradation | Medium | Limit batch size, run during off-peak hours |
| False positives (leads incorrectly flagged) | Medium | Refine filtering criteria based on business feedback |
| Credential exposure | High | Use environment variables and secret management |
| Concurrent execution | Low | Implement lock file mechanism |

---

## Success Metrics

1. **Coverage:** % of stale leads audited within 24 hours
2. **Accuracy:** % of correctly identified stale leads
3. **Performance:** Script execution time
4. **Reliability:** Successful execution rate

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Planning | 1 day | None |
| Phase 2: Module Development | 2-3 days | Phase 1 |
| Phase 3: Script Development | 2 days | Phase 2 |
| Phase 4: Deployment & Testing | 1-2 days | Phase 3 |
| **Total** | **6-8 days** | |

---

## Next Steps

1. ✅ Review and approve this implementation plan
2. ⏳ Create Odoo module structure
3. ⏳ Develop and test model extensions
4. ⏳ Create Python automation script
5. ⏳ Deploy to staging environment
6. ⏳ User acceptance testing
7. ⏳ Production deployment

---

**Document Version:** 1.0  
**Created:** March 4, 2026  
**Author:** Senior Odoo Technical Architect
