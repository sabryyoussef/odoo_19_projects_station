# MedTech Core - Installation Guide

## Prerequisites

### System Requirements
- **Odoo Version:** 19.0 or higher
- **Python:** 3.10+
- **PostgreSQL:** 13+
- **Operating System:** Windows, Linux, or macOS

### Required Odoo Modules
- `base` (pre-installed)
- `web` (pre-installed)
- `mail` (pre-installed)

## Installation Steps

### Method 1: Manual Installation (Development)

1. **Clone or Copy Module**
   ```bash
   cd /path/to/odoo/addons
   cp -r /path/to/medtech_core .
   ```

2. **Update Apps List**
   - Login to Odoo as Administrator
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "MedTech Core"

3. **Install Module**
   - Click **Install** button
   - Wait for installation to complete (takes 5-15 seconds)

4. **Verify Installation**
   - Navigate to **Settings** > **Users & Companies** > **Groups**
   - Confirm MedTech security groups exist:
     - MedTech / Operator
     - MedTech / Warehouse Supervisor
     - MedTech / Quality User
     - MedTech / Quality Manager
     - MedTech / Regulatory User
     - MedTech / Regulatory Manager
     - MedTech / Service Technician
     - MedTech / Auditor

### Method 2: Command Line Installation

```bash
# Navigate to Odoo root directory
cd /path/to/odoo

# Install module
python odoo-bin -c odoo.conf -d your_database -i medtech_core --stop-after-init

# Start server
python odoo-bin -c odoo.conf -d your_database
```

### Method 3: Docker Installation

```yaml
# docker-compose.yml
version: '3'
services:
  odoo:
    image: odoo:19.0
    volumes:
      - ./medtech_core:/mnt/extra-addons/medtech_core
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    depends_on:
      - db
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
```

```bash
docker-compose up -d
```

## Post-Installation Configuration

### 1. Assign Security Groups

Navigate to **Settings** > **Users & Companies** > **Users**

For each user, assign appropriate groups:

**Manufacturing Staff:**
- MedTech / Operator

**Warehouse Staff:**
- MedTech / Warehouse Supervisor

**Quality Team:**
- MedTech / Quality User (inspectors)
- MedTech / Quality Manager (QA managers)

**Regulatory Team:**
- MedTech / Regulatory User (documentation)
- MedTech / Regulatory Manager (submissions)

**Field Service:**
- MedTech / Service Technician

**Auditors:**
- MedTech / Auditor (read-only access)

### 2. Configure Company Settings (Future Enhancement)

This will be available in the MedTech Config views (currently commented out):
- Go to **MedTech** > **Configuration** > **Settings**
- Set regulatory framework (FDA, EU MDR, ISO 13485)
- Configure electronic signature requirements
- Set document retention periods

### 3. Enable Audit Trails

Audit trails are automatically enabled for any model inheriting `medtech.audit.mixin`.

To add audit trails to custom models:

```python
class YourModel(models.Model):
    _name = 'your.model'
    _inherit = ['medtech.audit.mixin']
```

## Troubleshooting

### Module Not Appearing in Apps List

**Solution:**
```bash
# Update module list
python odoo-bin -c odoo.conf -d your_database -u base --stop-after-init

# Restart server
python odoo-bin -c odoo.conf -d your_database
```

### Security Groups Not Created

**Solution:**
1. Check logs: `tail -f /path/to/odoo.log`
2. Verify `security/medtech_security.xml` file exists
3. Reinstall module:
   ```bash
   python odoo-bin -c odoo.conf -d your_database -u medtech_core --stop-after-init
   ```

### Permission Errors

**Solution:**
1. Verify user is assigned to appropriate security groups
2. Check record rules in **Settings** > **Technical** > **Security** > **Record Rules**
3. Review access rights in **Settings** > **Technical** > **Security** > **Access Rights**

### Menu Not Visible

**Solution:**
1. Verify you have at least one MedTech security group assigned
2. Clear browser cache (Ctrl+Shift+R)
3. Check if `views/medtech_menus.xml` is loaded

## Upgrade Instructions

### From Previous Version

```bash
# Backup database first!
pg_dump your_database > backup_$(date +%Y%m%d).sql

# Stop Odoo server
sudo systemctl stop odoo

# Update module files
cp -r /path/to/new/medtech_core /path/to/odoo/addons/

# Upgrade module
python odoo-bin -c odoo.conf -d your_database -u medtech_core --stop-after-init

# Start server
sudo systemctl start odoo
```

## Uninstallation

**Warning:** Uninstalling this module will affect all dependent MedTech modules.

```bash
# Command line
python odoo-bin -c odoo.conf -d your_database --uninstall medtech_core --stop-after-init
```

Or via UI:
1. Go to **Apps**
2. Find "MedTech Core"
3. Click **Uninstall**
4. Confirm deletion

## Development Setup

### For Module Development

1. **Enable Developer Mode**
   - Go to **Settings**
   - Scroll to bottom, click **Activate the developer mode**

2. **Install Developer Tools**
   ```bash
   pip install watchdog
   pip install odoo-test-helper
   ```

3. **Run Tests**
   ```bash
   python odoo-bin -c odoo.conf -d test_database --test-enable --stop-after-init -i medtech_core
   ```

4. **Debug Mode**
   ```bash
   python odoo-bin -c odoo.conf -d your_database --dev=all
   ```

## Production Deployment

### Recommended Settings

In `odoo.conf`:

```ini
[options]
# Workers for production
workers = 4

# Security
list_db = False
admin_passwd = YOUR_STRONG_PASSWORD

# Logging
logfile = /var/log/odoo/odoo.log
log_level = warn

# Performance
max_cron_threads = 2
db_maxconn = 64
```

### Systemd Service (Linux)

```ini
[Unit]
Description=Odoo 19 with MedTech ERP
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/usr/bin/python3 /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

## Support

For installation issues:
- Check logs: `tail -f /var/log/odoo/odoo.log`
- Verify file permissions
- Ensure all dependencies are installed
- Contact MedTech ERP Team for assistance
