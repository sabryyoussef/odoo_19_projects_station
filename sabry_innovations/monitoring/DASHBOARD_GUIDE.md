# Grafana Dashboard Guide

## 📊 Dashboard Created: "Odoo CRM Lead Audit Monitoring"

Your dashboard has been automatically provisioned and will appear in Grafana shortly!

---

## 🎯 Access Your Dashboard

1. Open Grafana: http://localhost:3000
2. Login: `admin` / `admin123`
3. Click **Dashboards** (left sidebar) or the four squares icon
4. Look for: **"Odoo CRM Lead Audit Monitoring"**

---

## 📈 Dashboard Panels

Your dashboard includes:

### 1. **System Health Monitoring**
- ✅ Prometheus Status
- ✅ Grafana Status  
- ✅ Discovered Targets
- ✅ Scrape Performance

### 2. **Database Information**
- 📊 PostgreSQL Database Tables (showing current grafana_db)
- 📦 Table sizes and schema info

### 3. **CRM Lead Audit Panels** (Placeholder - Ready for Odoo Connection)
- 📋 Lead Audit Status Table
- 🥧 Audit Status Distribution (Pie Chart)
- 📊 Leads Audited Over Time (Bar Chart)

---

## 🔗 Connect to Your Odoo Database

To show real Odoo/CRM data in the dashboard:

### Step 1: Update PostgreSQL Data Source

1. Go to **Connections** → **Data Sources**
2. Click on **PostgreSQL**
3. Update connection details:

```yaml
Host: your_odoo_database_host:5432
Database: your_odoo_db_name
User: your_odoo_db_user
Password: your_odoo_db_password
SSL Mode: disable (or as required)
```

4. Click **Save & test**

### Step 2: Edit Dashboard Queries

The dashboard has sample queries with commented Odoo queries. 

In each panel:
1. Click panel title → **Edit**
2. Uncomment the Odoo-specific SQL queries
3. Comment out the sample data queries
4. Click **Apply**

---

## 📝 Sample Queries Included

### Query 1: Lead Audit Status
```sql
SELECT 
  id,
  name as lead_name,
  user_id,
  x_is_audited,
  x_last_audit_date,
  create_date,
  probability,
  type
FROM crm_lead
WHERE type = 'lead'
  AND probability < 100
ORDER BY create_date DESC
LIMIT 50;
```

### Query 2: Audit Distribution
```sql
SELECT 
  CASE 
    WHEN x_is_audited = true THEN 'Audited'
    ELSE 'Not Audited'
  END as status,
  COUNT(*) as count
FROM crm_lead
WHERE type = 'lead' AND probability < 100
GROUP BY x_is_audited;
```

### Query 3: Audits Over Time
```sql
SELECT 
  DATE(x_last_audit_date) as time,
  COUNT(*) as audited_count
FROM crm_lead
WHERE x_last_audit_date >= NOW() - INTERVAL '7 days'
  AND x_is_audited = true
GROUP BY DATE(x_last_audit_date)
ORDER BY time;
```

---

## 🔄 Refresh the Dashboard

The dashboard is set to auto-refresh every **30 seconds**.

You can change this in the top-right corner of the dashboard.

---

## 🎨 Customize Your Dashboard

### Add New Panels
1. Click **Add** (top-right) → **Visualization**
2. Select data source (Prometheus or PostgreSQL)
3. Write your query
4. Choose visualization type
5. Click **Apply**

### Edit Existing Panels
1. Click panel title → **Edit**
2. Modify query or visualization settings
3. Click **Apply**

### Save Changes
- Click **Save dashboard** (top-right disk icon)
- Add a note about your changes

---

## 🚀 Advanced Features

### Variables
Add dashboard variables for:
- Date ranges
- User filters
- Lead stage filters

### Alerts
Set up alerts when:
- Too many stale leads detected
- Audit script fails
- Database connection issues

### Sharing
- Share dashboard link
- Create snapshot
- Export as JSON
- Set up scheduled reports

---

## 🔒 Connect to Actual Odoo Database

If your Odoo database is on the same network:

### Option 1: Direct Connection
Update PostgreSQL datasource:
```
Host: localhost:5432  (if Odoo DB is local)
Host: odoo_host:5432  (if remote)
Database: odoo_production
User: odoo_readonly_user  (recommended)
```

### Option 2: Via Docker Network
If Odoo is in Docker, add to docker-compose.yml:
```yaml
networks:
  default:
    name: odoo-monitoring
    external: false
```

---

## 📊 Dashboard Features

| Feature | Status |
|---------|--------|
| System Health | ✅ Active |
| Prometheus Metrics | ✅ Active |
| PostgreSQL Connection | ✅ Active |
| Sample Data | ✅ Showing |
| Odoo Connection | ⏳ Ready (needs config) |
| Auto-refresh | ✅ Every 30s |
| Dark Theme | ✅ Enabled |

---

## 🛠️ Troubleshooting

### Dashboard not showing?
```bash
# Restart Grafana
cd d:\odoo\odoo19\projects\sabry_innovations\monitoring
docker-compose restart grafana
```

### Can't see Odoo data?
- Check PostgreSQL datasource connection
- Verify database credentials
- Ensure network connectivity
- Check SQL query syntax

### Panel errors?
- Edit panel → Check query syntax
- Verify data source is selected
- Check field names match your schema

---

## 📚 Next Steps

1. ✅ View your dashboard in Grafana
2. ⏳ Connect to your Odoo database
3. ⏳ Customize queries for your needs
4. ⏳ Set up alerts
5. ⏳ Share with your team

---

**Dashboard is ready!** Go to http://localhost:3000 and explore! 🎉
