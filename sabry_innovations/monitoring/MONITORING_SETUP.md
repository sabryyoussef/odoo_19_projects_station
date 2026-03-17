# Grafana & Prometheus Monitoring Setup

## 📊 Quick Start

### Prerequisites
- Docker installed and running
- Docker Compose installed (included with Docker Desktop)

### Step 1: Start the Containers

```bash
cd d:\odoo\odoo19\projects\sabry_innovations\monitoring

# Start Grafana and Prometheus
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 2: Access Grafana

Open your browser and go to:
```
http://localhost:3000
```

**Login:**
- Username: `admin`
- Password: `admin123`

### Step 3: Verify Prometheus

Access Prometheus at:
```
http://localhost:9090
```

---

## 🎯 What's Running

- **Grafana** (Port 3000) - Visualization & dashboarding
- **Prometheus** (Port 9090) - Metrics collection & storage

---

## 📋 Common Commands

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f grafana
docker-compose logs -f prometheus

# Restart containers
docker-compose restart

# Remove containers and volumes (clean slate)
docker-compose down -v
```

---

## 🔍 Testing Connection

### Check if containers are running
```bash
docker ps
```

You should see both `grafana-odoo` and `prometheus-odoo` containers.

### Check Prometheus targets
Go to: http://localhost:9090/targets

You should see:
- `prometheus` job
- `grafana` job
- Status: UP

### Check Grafana health
Go to: http://localhost:3000/api/health

Should return: `{"status":"ok"}`

---

## 📈 Next Steps: Integrate with Your Automation Script

### Option 1: Add Metrics to Python Script

Install prometheus_client:
```bash
pip install prometheus-client
```

Add to `lead_audit_automation.py`:

```python
from prometheus_client import Counter, Gauge, start_http_server
import time

# Metrics
leads_audited = Counter('lead_audit_total', 'Total leads audited')
stale_leads_found = Gauge('stale_leads_count', 'Number of stale leads found')
audit_errors = Counter('audit_errors_total', 'Total audit errors')
script_runtime = Gauge('audit_script_runtime_seconds', 'Script execution time')

# Start metrics server on port 8000
start_http_server(8000)

# In your automation script, update metrics:
leads_audited.inc()
stale_leads_found.set(count)
audit_errors.inc()
```

Then uncomment in `prometheus.yml`:
```yaml
- job_name: 'lead_audit_automation'
  static_configs:
    - targets: ['localhost:8000']
```

### Option 2: Manual Dashboard Creation

1. Go to Grafana: http://localhost:3000
2. Create → Dashboard → New Panel
3. Select Prometheus as data source
4. Write queries like:
   ```promql
   up{job="prometheus"}
   ```

---

## 🚨 Troubleshooting

### Containers not starting
```bash
# Check detailed logs
docker-compose logs

# Ensure ports are free
netstat -ano | findstr :3000
netstat -ano | findstr :9090
```

### Can't connect to Grafana
- Wait 30 seconds after starting (health check)
- Clear browser cache or use incognito mode
- Check firewall settings

### Prometheus shows no data
- Wait 30 seconds for first scrape
- Go to http://localhost:9090/targets to verify jobs

### Permission denied errors
- On WSL/Linux: `sudo docker-compose up -d`

---

## 🛑 Cleanup

To remove all containers and data:
```bash
docker-compose down -v
```

To remove only containers (keep data):
```bash
docker-compose down
```

---

## 📚 Useful Links

- Grafana Docs: https://grafana.com/docs/
- Prometheus Docs: https://prometheus.io/docs/
- Docker: https://docs.docker.com/

---

## 🎯 Integration Checklist

- [ ] Docker containers started successfully
- [ ] Grafana accessible at localhost:3000
- [ ] Prometheus accessible at localhost:9090
- [ ] Prometheus targets showing UP status
- [ ] Datasource configured in Grafana
- [ ] Optional: Metrics integrated into automation script

---

**Status:** ✅ Ready to test!
