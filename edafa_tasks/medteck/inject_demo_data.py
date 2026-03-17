# -*- coding: utf-8 -*-
"""
MedTech ERP Demo Data Injection Script
Execute with: python odoo-bin shell -c odoo_conf/odoo.conf -d odoo19 < inject_demo_data.py
"""

import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

def inject_demo_data(env):
    """Inject comprehensive demo data for MedTech ERP use case"""
    
    _logger.info("="*80)
    _logger.info("Starting MedTech ERP Demo Data Injection")
    _logger.info("="*80)
    
    # Get admin user
    admin_user = env.ref('base.user_admin')
    _logger.info(f"Admin User ID: {admin_user.id}")
    
    # ========================================================================
    # 1. CREATE PRODUCT: Cardiac Pacemaker Model CP-2000
    # ========================================================================
    
    product_tmpl = env['product.template'].create({
        'name': 'Cardiac Pacemaker CP-2000',
        'type': 'product',
        'list_price': 15000.00,
        'standard_price': 8500.00,
        'tracking': 'serial',
        'description': 'Single-chamber cardiac pacemaker for bradycardia treatment',
    })
    
    product = product_tmpl.product_variant_id
    product.write({'default_code': 'CP-2000'})
    
    _logger.info(f"✓ Product Created - ID: {product.id}, Name: {product.name}")
    
    # ========================================================================
    # 2. DEVICE MASTER RECORD (Update product template with device fields)
    # ========================================================================
    
    product_tmpl.write({
        'is_medical_device': True,
        'device_family': 'Cardiac Pacemakers',
        'risk_class': 'class_iii',
        'intended_use': 'Single-chamber cardiac pacemaker for bradycardia treatment',
        'udi_di': '00312345678906',
    })
    device_master = product_tmpl  # Reference the product template as device master
    
    _logger.info(f"✓ Device Master Fields Updated - ID: {device_master.id}")
    
    # ========================================================================
    # 3. UDI RECORDS
    # ========================================================================
    
    # UDI-DI (Device Identifier)
    udi_di = env['medtech.udi'].create({
        'name': '(01)00312345678906',
        'product_id': product.id,
        'udi_type': 'udi_di',
        'issuing_agency': 'gs1',
        'primary_di': True,
        'active': True,
    })
    
    _logger.info(f"✓ UDI-DI Created - ID: {udi_di.id}")
    
    # UDI-PI for serial numbers
    udi_pis = []
    for sn_num in ['001', '002', '003']:
        udi_pi = env['medtech.udi'].create({
            'name': f'(01)00312345678906(21)CP2000-2601-{sn_num}(11)260110(17)280110',
            'product_id': product.id,
            'udi_type': 'udi_pi',
            'issuing_agency': 'gs1',
            'serial_number': f'CP2000-2601-{sn_num}',
            'production_date': '2026-01-10',
            'expiration_date': '2028-01-10',
            'lot_number': 'LOT-2601-A',
            'active': True,
        })
        udi_pis.append(udi_pi)
        _logger.info(f"✓ UDI-PI Created - SN: CP2000-2601-{sn_num}")
    
    # ========================================================================
    # 4. DEVICE HISTORY RECORDS
    # ========================================================================
    
    dhrs = []
    for sn_num in ['001', '002', '003']:
        dhr = env['medtech.dhr'].create({
            'name': f'DHR-2601-{sn_num}',
            'product_id': product.id,
            'serial_number': f'CP2000-2601-{sn_num}',
            'lot_number': 'LOT-2601-A',
            'state': 'closed',
            'manufacturing_date': '2026-01-10',
            'qc_pass': True,
            'qc_notes': 'All QC checks passed. Battery connection verified.',
        })
        dhrs.append(dhr)
        _logger.info(f"✓ DHR Created - {dhr.name}")
    
    # ========================================================================
    # 5. VENDOR PARTNER
    # ========================================================================
    
    vendor = env['res.partner'].create({
        'name': 'BatteryTech Solutions Inc.',
        'supplier_rank': 1,
        'company_type': 'company',
        'street': '500 Industrial Park Dr',
        'city': 'Boston',
        'zip': '02101',
        'country_id': env.ref('base.us').id,
        'phone': '+1-617-555-0100',
        'email': 'quality@batterytech.example.com',
    })
    
    _logger.info(f"✓ Vendor Created - ID: {vendor.id}, Name: {vendor.name}")
    
    # ========================================================================
    # 6. VENDOR CERTIFICATION
    # ========================================================================
    
    cert = env['medtech.vendor.certification'].create({
        'name': 'ISO 13485:2016 - BatteryTech',
        'partner_id': vendor.id,
        'certification_type': 'iso_13485',
        'status': 'valid',
        'issue_date': '2025-06-01',
        'expiry_date': '2028-06-01',
        'required_for_po': True,
    })
    
    _logger.info(f"✓ Vendor Certification Created - ID: {cert.id}")
    
    # ========================================================================
    # 7. NONCONFORMANCE
    # ========================================================================
    
    nc = env['medtech.nonconformance'].create({
        'name': 'NC-00001',
        'source': 'manufacturing',
        'severity': 'high',
        'description': (
            'Battery connection intermittent failure detected during final inspection of LOT-2601-A. '
            'Resistance measurements show variability in solder joints on battery terminals. '
            'Affects approximately 15 units from production run.'
        ),
        'detection_date': '2026-01-15',
        'detected_by_id': admin_user.id,
        'supplier_id': vendor.id,
        'state': 'contained',
        'affected_product_ids': [(6, 0, [product.id])],
        'root_cause': (
            'Root cause analysis identified: Supplier battery component (BatteryTech P/N BT-9900) has inconsistent terminal plating thickness. '
            'Incoming inspection did not catch the variation as it was within stated tolerances, but combined with our assembly process, '
            'it creates marginal solder joints that may degrade over time.'
        ),
        'containment_action': (
            'Immediate actions taken:\n'
            '1. Halted production using BatteryTech BT-9900 batteries from affected shipment (PO-2025-1234)\n'
            '2. Quarantined all finished goods from LOT-2601-A (15 units total, 12 already shipped)\n'
            '3. Initiated enhanced incoming inspection with terminal thickness verification\n'
            '4. Contacted BatteryTech QA department for investigation'
        ),
    })
    
    _logger.info(f"✓ Nonconformance Created - {nc.name}")
    
    # ========================================================================
    # 8. CAPA
    # ========================================================================
    
    # Get or create CAPA stage
    capa_stage = env['medtech.capa.stage'].search([('name', '=', 'Root Cause Analysis')], limit=1)
    if not capa_stage:
        capa_stage = env['medtech.capa.stage'].create({
            'name': 'Root Cause Analysis',
            'sequence': 2,
            'fold': False,
        })
    
    capa = env['medtech.capa'].create({
        'name': 'CAPA-00001',
        'source': 'nonconformance',
        'description': (
            'CAPA for NC-00001: Battery connection reliability improvement for CP-2000 pacemaker. '
            'Address supplier component quality variation and improve assembly process controls.'
        ),
        'priority': 'high',
        'stage_id': capa_stage.id,
        'responsible_user_id': admin_user.id,
        'approver_user_id': admin_user.id,
        'deadline_date': '2026-03-01',
        'state': 'in_progress',
        'root_cause_analysis': (
            'ROOT CAUSE ANALYSIS (5 Whys Method):\n'
            '1. Why did battery connections fail? - Solder joints had insufficient strength\n'
            '2. Why were solder joints weak? - Battery terminal plating thickness was inconsistent\n'
            '3. Why was plating inconsistent? - Supplier variation in electroplating process\n'
            '4. Why did supplier variation occur? - BatteryTech changed plating vendor without notification\n'
            '5. Why were we not notified? - No change control agreement in quality agreement\n\n'
            'ROOT CAUSE: Inadequate supplier change control process and missing contractual requirements'
        ),
        'corrective_action': (
            'CORRECTIVE ACTIONS:\n'
            '1. Return all BatteryTech batteries from affected shipment (PO-2025-1234)\n'
            '2. Update Quality Agreement with BatteryTech to require change notifications\n'
            '3. Add terminal thickness measurement to incoming inspection (IQP-005 rev B)\n'
            '4. Re-qualify BatteryTech as supplier with enhanced audit\n'
            '5. Implement statistical process control (SPC) on solder joint resistance\n'
            'Target Completion: Feb 28, 2026'
        ),
        'preventive_action': (
            'PREVENTIVE ACTIONS:\n'
            '1. Extend change control requirements to all critical component suppliers (15 vendors)\n'
            '2. Implement supplier portal for change notifications\n'
            '3. Add quarterly supplier audits for Class III device components\n'
            '4. Cross-train incoming inspection staff on critical characteristics\n'
            '5. Update FMEA for assembly process to include supplier variation risks\n'
            'Target Completion: April 30, 2026'
        ),
        'effectiveness_check_required': True,
        'effectiveness_check_date': '2026-04-15',
    })
    
    _logger.info(f"✓ CAPA Created - {capa.name}")
    
    # ========================================================================
    # 9. CUSTOMER & FIELD SERVICE
    # ========================================================================
    
    customer = env['res.partner'].create({
        'name': 'Memorial Hospital Cardiology Dept',
        'customer_rank': 1,
        'company_type': 'company',
        'street': '1000 Medical Center Drive',
        'city': 'Chicago',
        'zip': '60611',
        'country_id': env.ref('base.us').id,
        'phone': '+1-312-555-0200',
    })
    
    _logger.info(f"✓ Customer Created - {customer.name}")
    
    # Service Visit 1
    service1 = env['medtech.service.visit'].create({
        'name': 'SV-00001',
        'customer_id': customer.id,
        'visit_date': '2026-01-22',
        'visit_type': 'corrective',
        'service_type': 'repair',
        'serial_number': 'CP2000-2601-001',
        'issue_description': (
            'Device retrieved pre-implant during routine inventory check. '
            'Hospital reported intermittent battery indicator during pre-op testing.'
        ),
        'state': 'completed',
        'technician_notes': (
            'Device quarantined and returned to manufacturer. Battery connection resistance measured at 2.5 ohms (spec: <0.5 ohms). '
            'Clear indication of poor solder joint. Serial number matches LOT-2601-A. '
            'Hospital notified to check remaining inventory from same lot.'
        ),
    })
    
    _logger.info(f"✓ Service Visit Created - {service1.name}")
    
    # Service Visit 2
    service2 = env['medtech.service.visit'].create({
        'name': 'SV-00002',
        'customer_id': customer.id,
        'visit_date': '2026-01-22',
        'visit_type': 'corrective',
        'service_type': 'inspection',
        'serial_number': 'CP2000-2601-002',
        'issue_description': (
            'Pre-implant testing shows marginal battery performance. Request manufacturer inspection.'
        ),
        'state': 'completed',
        'technician_notes': (
            'Device inspected on-site. Battery connection exhibits higher than expected resistance. '
            'Device quarantined. Confirmed as LOT-2601-A. Recommend field action for all units from this lot.'
        ),
    })
    
    _logger.info(f"✓ Service Visit Created - {service2.name}")
    
    # ========================================================================
    # 10. RECALL
    # ========================================================================
    
    recall = env['medtech.recall'].create({
        'name': 'REC-00001',
        'recall_type': 'safety',
        'severity_class': 'class_ii',
        'reason': (
            'Voluntary recall of Cardiac Pacemaker CP-2000 units from manufacturing LOT-2601-A due to '
            'potential battery connection intermittent failure. Field reports and internal testing identified '
            'solder joint integrity issues that could lead to premature battery depletion or loss of pacing function. '
            'Risk assessment: Medium - devices are pre-implant inventory at hospitals, immediate patient risk is low.'
        ),
        'affected_lot_ids': 'LOT-2601-A',
        'fda_notification_required': True,
        'eu_mdr_notification_required': True,
        'state': 'in_progress',
        'initiated_date': '2026-01-25',
        'initiated_by_id': admin_user.id,
        'strategy': (
            'RECALL STRATEGY:\n'
            '1. Immediate notification to all customers who received LOT-2601-A (12 units distributed)\n'
            '2. Request return of all unused inventory within 30 days\n'
            '3. Provide replacement units from validated lots at no charge\n'
            '4. No implanted devices identified - all units in hospital inventory\n'
            '5. FDA notification via MedWatch (Class II recall)\n'
            '6. EU competent authority notification via Eudamed'
        ),
        'customer_notification_method': 'direct_email_phone',
        'effectiveness_check_required': True,
    })
    
    _logger.info(f"✓ Recall Created - {recall.name}")
    
    # ========================================================================
    # 11. QUARANTINE RECORDS
    # ========================================================================
    
    quarantine1 = env['medtech.quarantine'].create({
        'name': 'QRT-001-CP2000-2601-001',
        'reason': 'Recall REC-00001: Battery connection quality issue - LOT-2601-A',
        'status': 'released',
        'disposition': 'scrap',
        'disposition_date': '2026-01-26',
        'disposition_notes': (
            'Unit returned from Memorial Hospital. Destructive testing performed to validate root cause. '
            'Battery terminal solder joints exhibited poor wetting and voids. Scrapped per procedure SOP-QRT-001.'
        ),
    })
    
    quarantine2 = env['medtech.quarantine'].create({
        'name': 'QRT-002-CP2000-2601-002',
        'reason': 'Recall REC-00001: Battery connection quality issue - LOT-2601-A',
        'status': 'quarantined',
        'disposition': 'pending',
    })
    
    quarantine3 = env['medtech.quarantine'].create({
        'name': 'QRT-003-CP2000-2601-003',
        'reason': 'Recall REC-00001: Battery connection quality issue - LOT-2601-A',
        'status': 'quarantined',
        'disposition': 'pending',
    })
    
    _logger.info(f"✓ Quarantine Records Created - 3 total")
    
    # Commit all changes
    env.cr.commit()
    
    _logger.info("="*80)
    _logger.info("DEMO DATA INJECTION COMPLETE!")
    _logger.info("="*80)
    _logger.info(f"Product: {product.name} (ID: {product.id})")
    _logger.info(f"Device Master: ID {device_master.id}")
    _logger.info(f"Nonconformance: {nc.name}")
    _logger.info(f"CAPA: {capa.name}")
    _logger.info(f"Recall: {recall.name}")
    _logger.info(f"Service Visits: {service1.name}, {service2.name}")
    _logger.info("="*80)
    _logger.info("Navigate to MedTech menu to explore the workflow!")
    _logger.info("="*80)

# Main execution
if __name__ == '__main__':
    inject_demo_data(env)
