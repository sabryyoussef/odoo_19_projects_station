# MedTech ERP - Use Case Scenario & Workflow Guide

## 📋 USE CASE SCENARIO OVERVIEW

### **Cardiac Pacemaker Quality Crisis: From Manufacturing Defect to Recall**

**Product:** Cardiac Pacemaker Model CP-2000 (Class III Medical Device)  
**Manufacturer:** Your Company  
**Supplier:** BatteryTech Solutions Inc.  
**Criticality:** High (Implantable cardiac device)

---

## 🎬 SCENARIO TIMELINE

### **Week 1: Discovery (Jan 15-17, 2026)**
- **Jan 15**: Quality inspector discovers intermittent battery connections during final inspection
- **Jan 15**: Nonconformance NC-00001 raised (High Severity)
- **Jan 16**: Production halted for LOT-2601-A (15 units affected, 12 already shipped)
- **Jan 17**: CAPA-00001 initiated for root cause analysis
- **Jan 17**: Root cause identified: Supplier component quality variation

### **Week 2: Field Reports (Jan 22-23, 2026)**
- **Jan 22**: Memorial Hospital reports marginal battery performance (SN CP2000-2601-001)
- **Jan 22**: Second hospital reports similar issue (SN CP2000-2601-002)
- **Jan 23**: Field service team quarantines both devices

### **Week 3: Recall Decision (Jan 25-26, 2026)**
- **Jan 25**: Recall REC-00001 initiated (FDA Class II)
- **Jan 25**: Customer notifications sent to all affected sites
- **Jan 26**: Quarantine procedures activated for all LOT-2601-A units
- **Jan 26**: FDA MedWatch notification submitted

### **Ongoing: Remediation**
- CAPA actions in progress (supplier re-qualification, process improvements)
- Effectiveness checks scheduled for April 2026
- Vendor compliance review underway

---

## 💻 HOW TO INJECT DEMO DATA

### **Method 1: Using psql (PostgreSQL Command Line)**

```powershell
# From PowerShell in your Odoo directory
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP

# Run the SQL script
psql -U odoo -d odoo19 -f demo_data_scenario.sql
```

### **Method 2: Using pgAdmin**
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on `odoo19` database → Query Tool
4. Open file: `demo_data_scenario.sql`
5. Click **Execute** (F5)

### **Method 3: Direct Terminal**
```powershell
# Connect to database
psql -U odoo -d odoo19

# Copy-paste the SQL from demo_data_scenario.sql
# Or use: \i D:/odoo/odoo19/PROGECTS/MedTech_ERP/demo_data_scenario.sql
```

---

## 🔍 HOW TO VIEW THE WORKFLOW IN ODOO

### **Access Odoo**
1. Open browser: **http://localhost:8019**
2. Login with admin credentials
3. Look for **MedTech** menu in top navigation

---

## 📊 WORKFLOW NAVIGATION GUIDE

### **STEP 1: Start with the Product**
```
MedTech → Traceability → Device Master Records
```
**What to see:**
- ✅ Cardiac Pacemaker CP-2000
- Risk Class: III (Highest)
- Status: Active
- FDA Listing: D123456789
- CE Certificate: CE-2026-MDD-001234

**Actions:**
- Click on the record to see full device details
- Check "Intended Use" field
- Review regulatory approvals

---

### **STEP 2: Check UDI Registry**
```
MedTech → Traceability → UDI Registry
```
**What to see:**
- UDI-DI: (01)00312345678906 (Device Identifier)
- UDI-PI: Multiple production identifiers for each serial number
- Search for: `CP2000-2601-001`

**Actions:**
- Click on UDI-PI to see production details
- Check lot number: LOT-2601-A
- Verify expiration dates

---

### **STEP 3: Review Device History Records**
```
MedTech → Traceability → DHR (Device History Records)
```
**What to see:**
- DHR-2601-001 (Serial: CP2000-2601-001)
- DHR-2601-002 (Serial: CP2000-2601-002)
- DHR-2601-003 (Serial: CP2000-2601-003)
- All from LOT-2601-A
- Manufacturing date: Jan 10, 2026
- QC Status: Initially PASSED

**Actions:**
- Click on any DHR to see manufacturing details
- Check QC notes
- Look for serial number traceability

---

### **STEP 4: Investigate the Nonconformance**
```
MedTech → Quality & CAPA → Nonconformances
```
**What to see:**
- **NC-00001** (High Severity, Red highlight)
- Source: Manufacturing
- Status: Contained
- Detection Date: Jan 15, 2026

**Actions:**
1. Click on NC-00001
2. Read the **Description** tab:
   - Battery connection intermittent failure
   - Affects 15 units from LOT-2601-A
3. Check **Investigation** tab:
   - Root Cause Analysis (supplier component issue)
   - Containment actions taken
4. Look at **Affected Items**:
   - Linked product: CP-2000
5. Check **CAPAs** smart button (top right):
   - Should show 1 linked CAPA

---

### **STEP 5: Follow the CAPA Workflow**
```
MedTech → Quality & CAPA → CAPAs
```
**What to see:**
- **CAPA-00001** (High Priority)
- Kanban view with workflow stages
- Current stage: Root Cause Analysis
- Deadline: Mar 1, 2026
- Status: In Progress

**Actions:**
1. Click on CAPA-00001 card (or switch to list view)
2. Review **Root Cause Analysis** tab:
   - 5 Whys methodology documented
   - Root cause: Inadequate supplier change control
3. Read **Corrective Action** tab:
   - 5 specific actions listed
   - Target completion dates
4. Read **Preventive Action** tab:
   - Systemic improvements to prevent recurrence
5. Check **Effectiveness Check** tab:
   - Required: Yes
   - Check date: April 15, 2026
6. View **Approval History** (if visible)
7. Try workflow buttons:
   - You may see buttons for stage transitions depending on state

**Kanban View Navigation:**
- Drag CAPA card between stages to visualize workflow
- Each column represents a CAPA stage

---

### **STEP 6: Review Field Service Reports**
```
MedTech → Field Service History → Service Visits
```
**What to see:**
- **SV-00001** (Memorial Hospital, Jan 22)
  - Serial: CP2000-2601-001
  - Issue: Intermittent battery indicator
  - Status: Completed
- **SV-00002** (Memorial Hospital, Jan 22)
  - Serial: CP2000-2601-002
  - Issue: Marginal battery performance
  - Status: Completed

**Actions:**
1. Click on SV-00001
2. Read **Issue Description**
3. Check **Technician Notes**
4. See how customer complaints triggered investigation
5. Link to related recall (if smart button exists)

---

### **STEP 7: Examine the Recall**
```
MedTech → Recall Management → Recalls
```
**What to see:**
- **REC-00001** (Class II - FDA)
- Severity: Class II (Medium Risk)
- Status: In Progress
- Initiated: Jan 25, 2026
- Affected Lot: LOT-2601-A

**Actions:**
1. Click on REC-00001
2. Read **Reason** field (comprehensive recall rationale)
3. Check **Strategy** tab:
   - Customer notification plan
   - Return procedure
   - Replacement strategy
4. Review **Regulatory** tab:
   - FDA notification required: Yes
   - EU MDR notification required: Yes
5. Click **Quarantines** smart button:
   - Should show 3 quarantine records
6. Click **Notifications** smart button (if available):
   - Customer notification records

---

### **STEP 8: Check Quarantine Status**
```
MedTech → Recall Management → Quarantine
```
**What to see:**
- **QRT-001-CP2000-2601-001** (Released/Scrapped)
  - Destructive testing performed
  - Disposition: Scrap
- **QRT-002-CP2000-2601-002** (Quarantined/Pending)
- **QRT-003-CP2000-2601-003** (Quarantined/Pending)

**Actions:**
1. Click on QRT-001 (the scrapped one)
2. Read **Reason** for quarantine
3. Check **Disposition Notes**:
   - Validation testing details
   - Scrapping procedure reference
4. Note different **Disposition** values:
   - Scrap, Use As-Is, Rework, Return to Supplier

---

### **STEP 9: Verify Vendor Compliance**
```
MedTech → Vendor Compliance → Vendor Certifications
```
**What to see:**
- **BatteryTech Solutions Inc.**
- Certification: ISO 13485:2016
- Status: Valid
- Expiry: June 1, 2028
- Required for PO: Yes

**Actions:**
1. Click on the certification
2. Check expiry date
3. Notice this is the supplier involved in the NC
4. This demonstrates why vendor compliance tracking is critical

---

### **STEP 10: Review Audit Trail**
```
MedTech → MedTech Core → Audit Trail
```
**What to see:**
- Chronological log of all key events
- User: admin
- Models: medtech.nonconformance, medtech.capa, medtech.recall
- Operations: create, write
- Timestamps

**Actions:**
1. Search for specific events:
   - Filter by Model: medtech.nonconformance
   - Filter by Model: medtech.capa
   - Filter by Model: medtech.recall
2. Use **Group By → Date** to see timeline
3. Click on audit event to see:
   - What changed
   - Who made the change
   - When it happened
   - IP address

---

## 🔗 WORKFLOW CONNECTIONS TO OBSERVE

### **The Complete Chain:**
```
1. Manufacturing (DHR) 
   ↓
2. Quality Issue (Nonconformance NC-00001)
   ↓
3. Investigation (CAPA-00001)
   ↓
4. Field Reports (Service Visits SV-00001, SV-00002)
   ↓
5. Recall Decision (REC-00001)
   ↓
6. Quarantine (QRT-001, QRT-002, QRT-003)
   ↓
7. Supplier Action (Vendor certification review)
   ↓
8. Continuous Improvement (CAPA effectiveness checks)
```

### **Smart Buttons to Explore:**
Look for these clickable counters at the top of form views:
- **CAPAs** (on Nonconformance)
- **Quarantines** (on Recall)
- **Notifications** (on Recall)
- **Service Visits** (if linked to products)

---

## 🎯 TESTING WORKFLOW ACTIONS

### **Try These Interactive Features:**

#### **1. Move CAPA Through Stages**
```
Quality & CAPA → CAPAs → CAPA-00001 (Kanban view)
```
- Drag the CAPA card to next stage
- Watch state changes
- Try workflow buttons in form view

#### **2. Create Follow-up Actions**
```
From NC-00001 form:
```
- Click **"Create CAPA"** button (should create new CAPA linked to this NC)
- Log activities
- Add followers for notifications

#### **3. Search and Filter**
Try these searches:
- **Nonconformances:**
  - Filter by "High Severity"
  - Filter by "Open" status
  - Group by "Source"
  
- **CAPAs:**
  - Filter by "High Priority"
  - Filter by "Overdue"
  - Group by "Stage"
  
- **Recalls:**
  - Filter by "Class II"
  - Filter by "In Progress"

#### **4. Traceability Query**
```
MedTech → Traceability → Traceability Query
```
- Search for serial number: `CP2000-2601-001`
- Should show full genealogy
- Linked DHR, UDI, quarantine records

---

## 📈 REPORTING VIEWS TO CHECK

### **List Views:**
- Sort columns (click headers)
- Apply filters (top filter bar)
- Group by fields (Group By button)

### **Kanban Views:**
- CAPA workflow visualization
- Drag-and-drop stage changes

### **Search Views:**
- Advanced filters
- Saved searches
- Date ranges

---

## 🔐 COMPLIANCE DOCUMENTATION

### **What This Demonstrates:**

#### **FDA 21 CFR Part 820 (QSR):**
- ✅ Device History Records (820.184)
- ✅ Nonconformance handling (820.90)
- ✅ Corrective/Preventive Action (820.100)
- ✅ Complaint handling (820.198)
- ✅ Traceability (820.65)

#### **EU MDR 2017/745:**
- ✅ UDI implementation (Article 27)
- ✅ Post-market surveillance (Article 83-92)
- ✅ Field safety corrective actions (Article 89)
- ✅ Vigilance reporting

#### **ISO 13485:2016:**
- ✅ Design and development control
- ✅ Risk management integration
- ✅ Supplier management
- ✅ CAPA system

---

## 🚀 NEXT STEPS FOR EXPLORATION

1. **Create New Records:**
   - Add a new nonconformance
   - Create a CAPA
   - Open a service visit

2. **Test Workflows:**
   - Move CAPA through stages
   - Close a nonconformance
   - Update quarantine disposition

3. **Explore Relationships:**
   - Click all smart buttons
   - Follow links between records
   - Check audit trails

4. **Run Reports** (when implemented):
   - DHR PDF export
   - Recall effectiveness report
   - CAPA summary

---

## 📝 NOTES

- All demo data uses **admin** user (ID typically 2)
- Dates are set to January 2026 for chronological clarity
- Serial numbers follow pattern: CP2000-2601-XXX
- All regulatory numbers are fictional
- Customer/supplier information is demonstration only

---

## ⚠️ TROUBLESHOOTING

If you don't see data after injection:

1. **Refresh browser** (Ctrl+F5)
2. **Clear Odoo cache:**
   ```powershell
   Get-Process -Name python | Stop-Process -Force
   python odoo-bin -c odoo_conf\odoo.conf -d odoo19
   ```
3. **Check SQL execution:**
   - Look for errors in psql output
   - Verify RAISE NOTICE messages show IDs
4. **Verify sequences:**
   - NC-00001, CAPA-00001, REC-00001 should exist
5. **Check access rights:**
   - Login as admin user
   - Verify you have access to MedTech menu

---

## 📞 SUPPORT

For issues with demo data:
- Check `odoo.log` for errors
- Verify PostgreSQL connection
- Ensure all modules are updated
- Review access rights in Settings → Users

**Enjoy exploring your FDA/EU MDR compliant MedTech ERP system! 🏥**
