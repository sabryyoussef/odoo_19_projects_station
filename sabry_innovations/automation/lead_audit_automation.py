#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM Lead Audit Automation Script
==================================

This script connects to Odoo via erppeek to identify and audit stale CRM leads.

Stale Lead Criteria:
- Type is 'lead'
- Probability < 100 (not won)
- Not yet audited (x_is_audited = False)
- Created more than 48 hours ago
- No scheduled activities

Actions Performed:
1. Query Odoo for stale leads
2. Create audit activities assigned to responsible users
3. Mark leads as audited with timestamp

Author: Senior Odoo Technical Architect
Date: March 4, 2026
License: LGPL-3
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import erppeek

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f'lead_audit_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class OdooConfig:
    """Configuration class for Odoo connection parameters."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USERNAME')
        self.password = os.getenv('ODOO_PASSWORD')
        self.port = int(os.getenv('ODOO_PORT', '8069'))
        
        # Script configuration
        self.stale_hours = int(os.getenv('STALE_HOURS', '48'))
        self.max_leads = int(os.getenv('MAX_LEADS_PER_RUN', '500'))
        self.activity_type_id = int(os.getenv('ACTIVITY_TYPE_TODO', '4'))  # To Do activity type
        
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid
        """
        required_fields = ['url', 'db', 'username', 'password']
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            logger.error(f"Missing required environment variables: {', '.join(missing_fields)}")
            logger.error("Required: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD")
            return False
        
        return True


class LeadAuditAutomation:
    """Main automation class for auditing stale CRM leads."""
    
    def __init__(self, config: OdooConfig):
        """
        Initialize the automation with configuration.
        
        Args:
            config: OdooConfig instance with connection parameters
        """
        self.config = config
        self.client: Optional[erppeek.Client] = None
        self.lead_model = None
        self.activity_model = None
        self.activity_type_model = None
        
        # Statistics
        self.stats = {
            'total_found': 0,
            'activities_created': 0,
            'leads_audited': 0,
            'errors': 0,
        }
    
    def connect_to_odoo(self) -> bool:
        """
        Establish connection to Odoo using erppeek.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to Odoo at {self.config.url}")
            logger.info(f"Database: {self.config.db}")
            logger.info(f"User: {self.config.username}")
            
            self.client = erppeek.Client(
                server=self.config.url,
                db=self.config.db,
                user=self.config.username,
                password=self.config.password
            )
            
            # Test connection by getting server version
            version = self.client.server_version
            logger.info(f"Successfully connected to Odoo version: {version}")
            
            # Initialize models
            self.lead_model = self.client.model('crm.lead')
            self.activity_model = self.client.model('mail.activity')
            self.activity_type_model = self.client.model('mail.activity.type')
            
            logger.info("Models initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {str(e)}")
            logger.exception("Connection error details:")
            return False
    
    def fetch_stale_leads(self) -> List[int]:
        """
        Query Odoo for stale leads based on criteria.
        
        Returns:
            List[int]: List of lead IDs that need auditing
        """
        try:
            # Calculate threshold date (48 hours ago by default)
            threshold_date = datetime.now() - timedelta(hours=self.config.stale_hours)
            threshold_str = threshold_date.strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"Searching for leads created before: {threshold_str}")
            
            # Build search domain
            domain = [
                ('type', '=', 'lead'),
                ('probability', '<', 100),
                ('x_is_audited', '=', False),
                ('create_date', '<', threshold_str),
            ]
            
            # Search for leads
            lead_ids = self.lead_model.search(domain, limit=self.config.max_leads, order='create_date asc')
            
            # Filter out leads that have activities (erppeek limitation workaround)
            # We need to browse and check activity_ids
            stale_lead_ids = []
            for lead_id in lead_ids:
                lead = self.lead_model.browse(lead_id)
                if not lead.activity_ids:
                    stale_lead_ids.append(lead_id)
            
            self.stats['total_found'] = len(stale_lead_ids)
            logger.info(f"Found {len(stale_lead_ids)} stale leads requiring audit")
            
            return stale_lead_ids
            
        except Exception as e:
            logger.error(f"Error fetching stale leads: {str(e)}")
            logger.exception("Fetch error details:")
            self.stats['errors'] += 1
            return []
    
    def get_activity_type_id(self) -> int:
        """
        Get the 'To Do' activity type ID.
        
        Returns:
            int: Activity type ID for 'To Do' activities
        """
        try:
            # Try to find 'To Do' activity type
            activity_type_ids = self.activity_type_model.search([('name', '=', 'To Do')], limit=1)
            
            if activity_type_ids:
                return activity_type_ids[0]
            else:
                logger.warning("'To Do' activity type not found, using default ID from config")
                return self.config.activity_type_id
                
        except Exception as e:
            logger.warning(f"Error getting activity type: {str(e)}, using default")
            return self.config.activity_type_id
    
    def create_audit_activity(self, lead_id: int, user_id: int, lead_name: str) -> bool:
        """
        Create an audit activity for a specific lead.
        
        Args:
            lead_id: ID of the lead
            user_id: ID of the user to assign activity to
            lead_name: Name of the lead for logging
            
        Returns:
            bool: True if activity created successfully
        """
        try:
            activity_type_id = self.get_activity_type_id()
            
            # Prepare activity data
            activity_vals = {
                'res_model': 'crm.lead',
                'res_id': lead_id,
                'user_id': user_id,
                'activity_type_id': activity_type_id,
                'date_deadline': datetime.now().date().isoformat(),
                'summary': 'URGENT: Lead Audit Required - No activity detected.',
                'note': (
                    '<p>This lead has been flagged by the automated audit system.</p>'
                    f'<p><strong>Reason:</strong> Lead created more than {self.config.stale_hours} hours ago '
                    'with no scheduled activities.</p>'
                    '<p><strong>Required Action:</strong> Please review this lead and either:</p>'
                    '<ul>'
                    '<li>Schedule a follow-up activity</li>'
                    '<li>Update the lead stage</li>'
                    '<li>Mark the lead as won/lost if appropriate</li>'
                    '<li>Add notes explaining the current status</li>'
                    '</ul>'
                ),
            }
            
            # Create activity
            activity_id = self.activity_model.create(activity_vals)
            
            if activity_id:
                logger.info(f"Created activity {activity_id} for lead '{lead_name}' (ID: {lead_id})")
                self.stats['activities_created'] += 1
                return True
            else:
                logger.error(f"Failed to create activity for lead {lead_id}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"Error creating activity for lead {lead_id}: {str(e)}")
            logger.exception("Activity creation error details:")
            self.stats['errors'] += 1
            return False
    
    def mark_lead_audited(self, lead_id: int, lead_name: str) -> bool:
        """
        Mark a lead as audited with current timestamp.
        
        Args:
            lead_id: ID of the lead
            lead_name: Name of the lead for logging
            
        Returns:
            bool: True if update successful
        """
        try:
            # Update lead
            self.lead_model.write([lead_id], {
                'x_is_audited': True,
                'x_last_audit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            
            logger.info(f"Marked lead '{lead_name}' (ID: {lead_id}) as audited")
            self.stats['leads_audited'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error marking lead {lead_id} as audited: {str(e)}")
            logger.exception("Update error details:")
            self.stats['errors'] += 1
            return False
    
    def process_lead(self, lead_id: int) -> bool:
        """
        Process a single stale lead: create activity and mark as audited.
        
        Args:
            lead_id: ID of the lead to process
            
        Returns:
            bool: True if processing successful
        """
        try:
            # Browse lead to get details
            lead = self.lead_model.browse(lead_id)
            
            if not lead:
                logger.error(f"Lead {lead_id} not found")
                return False
            
            lead_name = lead.name or f"Lead #{lead_id}"
            user_id = lead.user_id.id if lead.user_id else None
            
            # Check if lead has an assigned user
            if not user_id:
                logger.warning(f"Lead '{lead_name}' (ID: {lead_id}) has no assigned user, skipping")
                return False
            
            logger.info(f"Processing lead '{lead_name}' (ID: {lead_id})")
            
            # Create audit activity
            activity_created = self.create_audit_activity(lead_id, user_id, lead_name)
            
            if activity_created:
                # Mark as audited
                return self.mark_lead_audited(lead_id, lead_name)
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing lead {lead_id}: {str(e)}")
            logger.exception("Processing error details:")
            self.stats['errors'] += 1
            return False
    
    def run(self) -> bool:
        """
        Main execution method for the automation.
        
        Returns:
            bool: True if execution completed successfully
        """
        logger.info("=" * 80)
        logger.info("CRM Lead Audit Automation - Starting")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        try:
            # Connect to Odoo
            if not self.connect_to_odoo():
                logger.error("Failed to connect to Odoo, aborting")
                return False
            
            # Fetch stale leads
            stale_lead_ids = self.fetch_stale_leads()
            
            if not stale_lead_ids:
                logger.info("No stale leads found, nothing to process")
                return True
            
            # Process each lead
            logger.info(f"Starting to process {len(stale_lead_ids)} leads...")
            
            for idx, lead_id in enumerate(stale_lead_ids, 1):
                logger.info(f"Processing lead {idx}/{len(stale_lead_ids)}")
                self.process_lead(lead_id)
            
            # Print summary
            logger.info("=" * 80)
            logger.info("Execution Summary:")
            logger.info(f"  Stale leads found: {self.stats['total_found']}")
            logger.info(f"  Activities created: {self.stats['activities_created']}")
            logger.info(f"  Leads marked as audited: {self.stats['leads_audited']}")
            logger.info(f"  Errors encountered: {self.stats['errors']}")
            logger.info("=" * 80)
            
            success_rate = (self.stats['leads_audited'] / self.stats['total_found'] * 100) if self.stats['total_found'] > 0 else 0
            logger.info(f"Success rate: {success_rate:.2f}%")
            
            return self.stats['errors'] == 0
            
        except Exception as e:
            logger.error(f"Unexpected error during execution: {str(e)}")
            logger.exception("Execution error details:")
            return False
        
        finally:
            logger.info("CRM Lead Audit Automation - Finished")


def main():
    """Main entry point for the script."""
    
    # Load configuration
    config = OdooConfig()
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Create automation instance
    automation = LeadAuditAutomation(config)
    
    # Run automation
    success = automation.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
