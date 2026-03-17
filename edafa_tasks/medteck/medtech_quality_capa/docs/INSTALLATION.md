# MedTech Quality CAPA - Installation Guide

## Prerequisites

- **Odoo 19.0+**
- **medtech_core** module already installed
- **Quality Control** (optional, for integration)

## Installation

### Step 1: Install via Apps Menu

1. Go to **Apps** > Update Apps List
2. Search "MedTech Quality CAPA"
3. Click **Install**
4. Wait 10-15 seconds

### Step 2: Verify Installation

Check that these menus appear under **MedTech > Quality**:
- Nonconformances
- CAPAs
- CAPA Dashboard
- Configuration

### Step 3: Configure Access Rights

Assign users to appropriate groups:
- **Quality User:** Can create NCRs and CAPAs
- **Quality Manager:** Can approve CAPAs
- **Regulatory Manager:** Can signoff critical CAPAs

### Step 4: Configure Sequences

Navigate to **Settings** > **Technical** > **Sequences**

Verify these exist:
- `medtech.nonconformance` (Format: NCR/YYYY/0001)
- `medtech.capa` (Format: CAPA/YYYY/0001)

## Post-Installation Setup

### 1. Define Root Cause Categories

Create common root cause categories for your organization:
- Material defect
- Process deviation
- Equipment failure
- Human error
- Design flaw
- Software bug
- Environmental factor

### 2. Set CAPA Thresholds

Define when CAPAs are mandatory:
- All Critical NCRs → Automatic CAPA
- Multiple Minor NCRs (same root cause) → CAPA
- Customer complaints → CAPA evaluation

### 3. Configure Effectiveness Check Schedule

Typical timeline:
- Immediate actions: 1 week effectiveness check
- Process changes: 30 days effectiveness check
- Design changes: 90 days effectiveness check

## Troubleshooting

**Dashboard not loading?**
- Clear browser cache (Ctrl+Shift+R)
- Check browser console for JavaScript errors
- Verify OWL component loaded: Check static/src/js/capa_dashboard.js

**CAPAs not creating?**
- Check user has Quality User group
- Verify sequences configured
- Check server logs for errors

**Approval buttons missing?**
- Verify user has Quality Manager group
- Check CAPA state (must be "Pending Approval")
- Review record rules in Security settings
