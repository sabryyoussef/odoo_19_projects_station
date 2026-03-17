# 🚀 Quick Git Commands - Daily Workflow

**Project**: MedTech ERP  
**Repository**: https://github.com/sabryyoussef/edafa_MedTech  
**Working Directory**: `D:\odoo\odoo19\PROGECTS\MedTech_ERP\`

---

## 📋 After Every Phase Completion

### **1-Liner Quick Push**
```powershell
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP; git add .; git commit -m "Phase X.Y: Description"; git push origin main
```

### **Step-by-Step (Recommended)**

```powershell
# Navigate to project
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP

# Check what changed
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Phase 9.2: Recall Dashboard OWL Component"

# Push to GitHub
git push origin main
```

---

## ✅ Pre-Push Checklist

Before every `git push`:

```powershell
# 1. Test module update
cd D:\odoo\odoo19
python odoo-bin -c odoo_conf\odoo.conf -d odoo19 -u module_name --stop-after-init

# 2. Check for errors in logs
if ($LASTEXITCODE -eq 0) { 
    Write-Host "✅ Module updated successfully" -ForegroundColor Green 
} else { 
    Write-Host "❌ Update failed - Check logs" -ForegroundColor Red 
}

# 3. Go back to project folder
cd PROGECTS\MedTech_ERP

# 4. Commit and push
git add .
git commit -m "Phase X.Y: Feature description"
git push origin main
```

---

## 📝 Commit Message Templates

### **Feature Completion**
```
Phase 9.2: Recall Dashboard OWL Component

- Created recall_dashboard.js with live KPI tracking
- Added active recalls by severity/class visualization
- Implemented affected population calculator
- Linked recall events to quarantine records

Affected modules: medtech_recall
Testing: Dashboard renders, KPIs update real-time
FDA/MDR Impact: Medium (recall reporting enhancement)
```

### **Bug Fix**
```
Bugfix: Fix DHR genealogy tree computation

- Fixed recursive loop in compute_genealogy_tree() method
- Added null checks for component_dhr_id references
- Updated OWL template to handle empty components array

Affected modules: medtech_traceability
Testing: Genealogy trace works for 3-level component hierarchy
FDA/MDR Impact: None (internal fix)
```

### **Documentation Update**
```
Docs: Update IMPLEMENTATION_PLAN.md with Phase 11-14

- Added Phase 11: Compliance Analytics specifications
- Added Phase 12: ATP Logic implementation plan
- Updated project metrics (60% → 40% remaining)

Affected modules: None (documentation only)
Testing: N/A
FDA/MDR Impact: None
```

---

## 🔄 Daily Workflow Summary

| Time | Action | Command |
|------|--------|---------|
| **Start of day** | Pull latest changes | `git pull origin main` |
| **During development** | Check status frequently | `git status` |
| **After phase complete** | Test in Odoo | `python odoo-bin -c odoo_conf\odoo.conf -d odoo19 -u module_name --stop-after-init` |
| **After successful test** | Commit & push | `git add .; git commit -m "..."; git push origin main` |
| **End of day** | Verify push succeeded | Visit https://github.com/sabryyoussef/edafa_MedTech |

---

## 🆘 Emergency Commands

### **Undo Last Commit (Keep Changes)**
```powershell
git reset --soft HEAD~1
```

### **Discard All Uncommitted Changes**
```powershell
git reset --hard HEAD  # ⚠️ DANGER: Loses all changes!
```

### **Check Commit History**
```powershell
git log --oneline -10
```

### **View What Changed in Last Commit**
```powershell
git show HEAD
```

### **Create Backup Before Risky Operation**
```powershell
git branch backup-$(Get-Date -Format "yyyyMMdd-HHmm")
```

---

## 📁 Repository Links

- **GitHub**: https://github.com/sabryyoussef/edafa_MedTech
- **Local**: D:\odoo\odoo19\PROGECTS\MedTech_ERP\
- **Detailed Workflow**: See `.git-workflow.md`

---

## 🎯 Common Scenarios

### **Scenario A: Just finished Phase 9.2**
```powershell
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP
git add .
git commit -m "Phase 9.2: Recall Dashboard OWL Component"
git push origin main
```

### **Scenario B: Fixed a bug in existing code**
```powershell
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP
git add medtech_traceability/models/medtech_dhr.py
git commit -m "Bugfix: Fix DHR genealogy null reference error"
git push origin main
```

### **Scenario C: Updated documentation only**
```powershell
cd D:\odoo\odoo19\PROGECTS\MedTech_ERP
git add IMPLEMENTATION_PLAN.md
git commit -m "Docs: Update Phase 11 specifications"
git push origin main
```

---

## ✨ Pro Tips

1. **Commit frequently**: Better to have many small commits than one giant commit
2. **Test before commit**: Always run module update and check logs
3. **Descriptive messages**: Future you will thank present you
4. **Check GitHub**: Visit repo after push to verify files updated
5. **Read .git-workflow.md**: Full details on best practices

---

**Last Updated**: February 25, 2026  
**Quick Help**: See [.git-workflow.md](.git-workflow.md) for complete guide

---

_"Commit early, commit often, push daily."_
