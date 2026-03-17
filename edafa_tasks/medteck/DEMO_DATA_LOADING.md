# Demo Data Loading Instructions

## Why Demo Data Doesn't Appear

Odoo only loads demo data (`'demo': [...]` in manifest) during:
1. **Initial module installation** with `-i` flag
2. **Database creation** with `--demo=all` flag

Since the module is already installed, demo data won't load automatically during `-u` (update).

## Solution: Load Demo Data as Regular Data

We have 2 options:

### Option 1: Move Demo Data to Regular Data (Recommended)

This makes the demo data load like regular configuration data.

**Step 1:** Update medtech_core manifest
```python
# In medtech_core/__manifest__.py, move demo data to data section:
'data': [
    # Security
    'security/medtech_security.xml',
    'security/ir.model.access.csv',
    # Data
    # Views
    'views/medtech_audit_views.xml',
    # Menus
    'views/medtech_menus.xml',
    # Demo/Sample Data
    'demo/demo_data.xml',  # Move this from 'demo' section to here
],
# Remove or comment out the demo section:
# 'demo': [
#     'demo/demo_data.xml',
# ],
```

**Step 2:** Update the module
```powershell
python odoo-bin -c odoo_conf/odoo.conf -d odoo19 -u medtech_core --stop-after-init
```

### Option 2: Uninstall and Reinstall Module

This forces Odoo to load demo data, but **this will delete any existing data** in the module.

```powershell
# Uninstall
python odoo-bin -c odoo_conf/odoo.conf -d odoo19 -u medtech_core --stop-after-init

# Then reinstall with -i flag
python odoo-bin -c odoo_conf/odoo.conf -d odoo19 -i medtech_core --stop-after-init
```

### Option 3: Create New Database with Demo Data

```powershell
# Stop current server
# Create new database with demo data enabled
python odoo-bin -c odoo_conf/odoo.conf -d odoo19_demo --init=medtech_core,medtech_traceability,medtech_quality_capa,medtech_recall,medtech_vendor_compliance,medtech_field_service_history --stop-after-init --load-language=en_US --demo=all
```

## Recommended Approach

**Use Option 1** - Move demo data to the data section. This way:
- ✅ Demo data loads during normal updates
- ✅ No risk of data loss
- ✅ Can be used as sample/training data
- ✅ Can be enhanced or modified later

## After Loading Demo Data

Once loaded, you should see:
- **Product:** Cardiac Pacemaker CP-2000
- **Device Master:** FDA D123456789
- **UDI Records:** 4 records (1 DI + 3 PI)
- **DHRs:** 3 records for LOT-2601-A
- **Vendor:** BatteryTech Solutions Inc.
- **Nonconformance:** NC-00001
- **CAPA:** CAPA-00001
- **Service Visits:** SV-00001, SV-00002
- **Recall:** REC-00001
- **Quarantine:** QRT-001, QRT-002, QRT-003

Navigate to: MedTech > Quality & CAPA > Nonconformances to verify NC-00001 exists.
