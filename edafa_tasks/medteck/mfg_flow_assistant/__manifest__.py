{
    "name": "Manufacturing Flow Assistant",
    "version": "19.0.1.0.0",
    "summary": "Step-by-step manufacturing preparation assistant",
    "category": "Manufacturing",
    "author": "Edafa Tasks",
    "license": "LGPL-3",
    "depends": [
        "mrp",
        "stock",
        "quality_mrp_workorder",
        "medtech_traceability",
        "medtech_quality_capa",
        "medtech_recall",
        "medtech_field_service_history",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mfg_flow_wizard_views.xml",
    ],
    "application": False,
    "installable": True,
}
