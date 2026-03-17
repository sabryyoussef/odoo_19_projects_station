# CRM Lead Audit Automation - Quick Reference

## 🚀 Installation Summary

### 1. Odoo Module Installation
```bash
# Copy module to addons
cp -r crm_lead_audit /path/to/odoo/addons/

# Restart Odoo and install via UI
# Apps → Update Apps List → Search "CRM Lead Audit" → Activate
```

### 2. Automation Script Setup
```bash
cd automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your Odoo credentials
```

### 3. Test Run
```bash
python lead_audit_automation.py
```

### 4. Schedule (Choose One)

**Linux Crontab:**
```bash
crontab -e
# Add: 0 8 * * * cd /path/to/automation && ./run_lead_audit.sh
```

**Windows Task Scheduler:**
- See DEPLOYMENT_GUIDE.md for detailed steps
- Run: `automation\run_lead_audit.bat` daily at 8 AM

**Jenkins:**
- Import `Jenkinsfile`
- Configure credentials
- Set trigger: cron('0 8 * * *')

---

## 📋 Environment Variables

Required in `.env` file:
```
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=automation_user@company.com
ODOO_PASSWORD=your_password
```

Optional:
```
STALE_HOURS=48
MAX_LEADS_PER_RUN=500
```

---

## 🎯 How It Works

1. **Every 48 hours** after lead creation
2. **If no activities** scheduled
3. **Script creates** "To Do" activity for salesperson
4. **Lead marked** as audited with timestamp

---

## 📊 Where to Find Things in Odoo

- **Audit Fields:** CRM Lead Form → "Audit Information" tab (Sales Managers only)
- **Stale Leads:** CRM → Leads → Stale Leads (menu)
- **Filters:** CRM Leads → Filters → "Stale Leads", "Not Audited", "Audited"
- **Status Badges:** CRM Lead Form → Header buttons

---

## 🔍 Monitoring

**Check logs:**
```bash
# Linux
tail -f automation/logs/lead_audit_$(date +%Y%m%d).log

# Windows
Get-Content automation\logs\lead_audit_$(Get-Date -Format 'yyyyMMdd').log -Wait
```

**Key metrics in logs:**
- Stale leads found
- Activities created
- Leads marked as audited
- Success rate

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to Odoo | Check ODOO_URL, verify Odoo is running |
| Auth failed | Verify ODOO_USERNAME and ODOO_PASSWORD |
| No leads found | Check if leads exist, verify module installed |
| Module import error | Ensure erppeek installed: `pip install erppeek` |

---

## 📁 File Structure

```
sabry_innovations/
├── README.md                    ← Start here
├── IMPLEMENTATION_PLAN.md       ← Technical details
├── DEPLOYMENT_GUIDE.md          ← Deployment instructions
├── crm_lead_audit/              ← Odoo module
└── automation/                  ← Python scripts
    ├── lead_audit_automation.py ← Main script
    ├── .env                     ← Your credentials (create from .env.example)
    └── logs/                    ← Log files
```

---

## ✅ Pre-Deployment Checklist

- [ ] Odoo module installed and activated
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] .env file configured with credentials
- [ ] Test run successful
- [ ] Scheduler configured (cron/Task Scheduler/Jenkins)
- [ ] Log directory writable
- [ ] Backup taken

---

## 🔒 Security Checklist

- [ ] Dedicated automation user created in Odoo
- [ ] Minimal permissions granted
- [ ] .env file NOT committed to git
- [ ] Strong password used
- [ ] HTTPS enabled for production
- [ ] Credentials stored securely

---

## 📞 Support Resources

1. **Main Documentation:** README.md
2. **Installation Guide:** DEPLOYMENT_GUIDE.md
3. **Technical Specs:** IMPLEMENTATION_PLAN.md
4. **Module Docs:** crm_lead_audit/README.md
5. **Script Logs:** automation/logs/

---

## 🎓 Training for Sales Team

### For Salespeople
1. You'll receive "URGENT: Lead Audit Required" activities for stale leads
2. Complete the activity by following up on the lead
3. Schedule future activities to prevent re-auditing

### For Sales Managers
1. Access "Stale Leads" menu to see all leads needing attention
2. View "Audit Information" tab on any lead
3. Use filters to find audited/non-audited leads
4. Monitor team responsiveness to audit activities

---

**🌟 Success!** Your CRM Lead Audit Automation is now ready to ensure no lead falls through the cracks!

For detailed help, see the full documentation files listed above.
