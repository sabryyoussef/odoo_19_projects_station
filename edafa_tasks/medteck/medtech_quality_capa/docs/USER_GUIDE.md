# MedTech Quality CAPA - User Guide

## Creating a Nonconformance Report (NCR)

### Scenario: Failed Inspection

1. **Navigate:** MedTech > Quality > Nonconformances > Create
2. **Fill Required Fields:**
   - **Description:** "Dimension B out of specification (12.3mm, spec: 12.0±0.2mm)"
   - **Severity:** Major
   - **Product:** Select affected product
   - **Lot/Serial:** Enter traceability info
3. **Root Cause Analysis:**
   - Use 5 Whys technique
   - Document findings
4. **Disposition Decision:**
   - **Scrap:** If unusable
   - **Rework:** If can be corrected
   - **Use-As-Is:** If acceptable (requires waiver)
   - **Return to Supplier:** If vendor issue
5. **Determine if CAPA Needed:**
   - Click "Create CAPA" if systemic issue
   - Otherwise, close NCR after disposition

## Creating a CAPA

### From NCR

1. Open NCR
2. Click "Create CAPA" button
3. CAPA auto-populates with NCR info

### Standalone CAPA

1. **Navigate:** MedTech > Quality > CAPAs > Create
2. **CAPA Type:**
   - **Corrective:** Fix existing problem
   - **Preventive:** Prevent potential problem
   - **Both:** Fix and prevent
3. **Root Cause:** Document thoroughly
4. **Corrective Action:**
   - What specifically will be done
   - Who is responsible
   - Target completion date
5. **Preventive Action:**
   - How to prevent recurrence
   - Process changes needed
   - Training requirements
6. **Effectiveness Check:**
   - Set review date
   - Define success criteria
7. **Save and Submit for Approval**

## CAPA Workflow

```
Draft → In Progress → Pending Approval → Approved → 
Effectiveness Check → Closed (or Re-opened if ineffective)
```

### As CAPA Owner

1. **Draft:** Fill all required fields
2. **Submit for Approval:** Click button
3. **Implement Actions:** Complete corrective/preventive actions
4. **Request Effectiveness Check:** When ready

### As Quality Manager

1. **Receive Notification:** "CAPA awaiting approval"
2. **Review Thoroughly:**
   - Root cause makes sense?
   - Actions address root cause?
   - Timeline realistic?
3. **Approve or Reject:**
   - Approve: CAPA proceeds
   - Reject: Returns to owner with comments

### Effectiveness Check

1. **When Due:** System sends reminder
2. **Perform Verification:**
   - Check if issue recurred
   - Review metrics
   - Interview staff
3. **Record Results:**
   - **Pass:** Close CAPA
   - **Fail:** Re-open CAPA, refine actions

## Using the CAPA Dashboard

### Access Dashboard

**MedTech > Quality > CAPA Dashboard**

### Dashboard Sections

**KPI Cards (Top Row):**
- Total CAPAs
- Open CAPAs
- Overdue CAPAs (red if > 0)
- Closed This Month
- Avg Time to Close (days)
- Effectiveness Rate (%)

**CAPA Pipeline (Middle):**
Pie chart showing distribution:
- Draft
- In Progress
- Pending Approval
- Approved
- Effectiveness Check
- Closed

**Action Lists (Bottom):**
- **Overdue CAPAs:** Requires immediate attention
- **Effectiveness Checks Due:** Schedule reviews
- **Recent CAPAs:** Last 10 created

### Filtering

Click chart segments to filter:
- Click "Overdue" slice → Shows only overdue CAPAs
- Click "In Progress" → Shows all in-progress

## Use Cases

### Use Case 1: Product Defect Found During Final Inspection

**Situation:** Inspector finds crack in 10% of units from Lot ABC123

**Steps:**
1. **Create NCR:**
   - Description: "Cracks found in housing—10% defect rate"
   - Severity: Critical
   - Lot: ABC123
   - Disposition: Scrap (100 units)

2. **Immediate Containment:**
   - Quarantine entire lot
   - Inspect all other lots from same production run

3. **Create CAPA:**
   - Root Cause: Injection molding pressure too high
   - Corrective: Adjust molding parameters
   - Preventive: Implement process monitoring, operator training

4. **Effectiveness Check (30 days):**
   - Review next 1000 units
   - No cracks found
   - Close CAPA

### Use Case 2: Customer Complaint Trend

**Situation:** Three customer complaints about device software crash

**Steps:**
1. **Create CAPA (Preventive):**
   - Type: Both (Corrective + Preventive)
   - Root Cause: Software memory leak
   - Corrective: Release firmware update
   - Preventive: Implement stress testing in QA

2. **Link Related Records:**
   - Add links to 3 customer complaint records
   - Reference software test reports

3. **Implementation:**
   - Develop and validate firmware fix
   - Notify customers of available update
   - Update design controls

4. **Effectiveness Check (90 days):**
   - Monitor complaint database
   - No new complaints
   - Close CAPA

## Best Practices

### Root Cause Analysis

**Use 5 Whys:**
```
Problem: Part failed leak test
Why? Seal was defective
Why? Seal had visible crack
Why? Molding temperature too low
Why? Thermocouple miscalibrated
Why? Calibration schedule not followed
Root Cause: Inadequate calibration procedure
```

### CAPA Writing Tips

✅ **Good CAPA:**
- "Implement weekly calibration checks for all thermocouples per SOP-CAL-001. Training completed by 2026-03-15. Verify with calibration logbook review at 30 days."

❌ **Poor CAPA:**
- "Fix the problem. Train people better."

### Effectiveness Criteria

Define measurable success:
- ✅ "Zero defects in next 500 units"
- ✅ "Cycle time reduced by 15%"
- ✅ "100% operator quiz scores > 90%"
- ❌ "Things get better"

## FAQ

**Q: Do I need a CAPA for every NCR?**  
A: No. Single isolated incidents may not require CAPA. Trends or critical issues always need CAPA.

**Q: Can I have multiple CAPAs for one NCR?**  
A: Yes. Complex issues may need multiple correction paths.

**Q: What if CAPA fails effectiveness check?**  
A: Re-open CAPA, revise actions, implement additional measures.

**Q: How long to keep closed CAPAs?**  
A: Minimum 3 years per FDA. Some critical device CAPAs: life of device + 2 years.

**Q: Can I delete a CAPA?**  
A: No. Cancel it instead (provides audit trail).
