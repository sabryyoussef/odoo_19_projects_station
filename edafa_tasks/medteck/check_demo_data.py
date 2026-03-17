#!/usr/bin/env python3
# Simplified demo data loader - execute this file with Odoo shell

try:
    # Check if demo data was loaded
    Product = env['product.product']
    pacemaker = Product.search([('name', '=', 'Cardiac Pacemaker CP-2000')], limit=1)
    
    if pacemaker:
        print(f"\n✓ DEMO DATA ALREADY LOADED!")
        print(f"  Product: {pacemaker.name} (ID: {pacemaker.id})")
        
        # Count all demo records
        nc = env['medtech.nonconformance'].search([('name', '=', 'NC-00001')])
        capa = env['medtech.capa'].search([('name', '=', 'CAPA-00001')])
        recall = env['medtech.recall'].search([('name', '=', 'REC-00001')])
        dhrs = env['medtech.dhr'].search([('lot_number', '=', 'LOT-2601-A')])
        
        print(f"  Nonconformance: {nc.name if nc else 'NOT FOUND'}")
        print(f"  CAPA: {capa.name if capa else 'NOT FOUND'}")
        print(f"  Recall: {recall.name if recall else 'NOT FOUND'}")
        print(f"  DHRs for LOT-2601-A: {len(dhrs)} records")
        print(f"\n  Navigate to MedTech menu in Odoo to explore!")
    else:
        print("\n! Demo data NOT found. Installing...")
        print("  This means the module needs to be reinstalled with demo data.")
        print("  The demo data XML file is in: medtech_core/demo/demo_data.xml")
        print("  It will be loaded when you upgrade/reinstall the module.")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
