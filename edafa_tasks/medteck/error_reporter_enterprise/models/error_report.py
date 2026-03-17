from odoo import models, fields, api


class ErrorReport(models.Model):
    _name = 'error.report'
    _description = 'Error Report for Testing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Error Title', required=True, tracking=True,
                      help='Brief title for the error')
    
    reporter_id = fields.Many2one('res.users', string='Reporter', 
                                 required=True, default=lambda self: self.env.user,
                                 tracking=True, help='Who reported this error')
    
    report_date = fields.Datetime(string='Report Date', required=True, 
                                  default=fields.Datetime.now, tracking=True,
                                  help='When the error was reported')
    
    error_location = fields.Char(string='Location/Menu', 
                                 help='Where did the error occur? (e.g., Sales → Invoices)')
    
    current_url = fields.Char(string='Current URL', 
                             help='Automatically captured URL when error occurred')
    
    description = fields.Html(string='What Happened?', required=True,
                             help='Describe what you were trying to do when the error occurred')
    
    error_message = fields.Text(string='Error Message',
                               help='Copy and paste the exact error message here')
    
    steps_to_reproduce = fields.Html(string='Steps to Reproduce',
                                     help='Step-by-step: how to make this error happen again?')
    
    impact = fields.Selection([
        ('critical', '🔴 CRITICAL - Blocks work completely'),
        ('high', '🟡 HIGH - Major feature broken'),
        ('medium', '🟢 MEDIUM - Workaround available'),
        ('low', '⚪ LOW - Minor issue'),
    ], string='Impact Level', required=True, default='medium', tracking=True,
       help='How severe is this error?')
    
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('wont_fix', 'Won\'t Fix'),
        ('duplicate', 'Duplicate'),
    ], string='Status', required=True, default='new', tracking=True,
       help='Current status of this error report')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1', tracking=True)
    
    module_name = fields.Char(string='Module', 
                              help='Which module has the error? (if known)')
    
    record_reference = fields.Char(string='Record Reference',
                                  help='Invoice number, project name, etc.')
    
    browser_info = fields.Char(string='Browser',
                              help='Chrome, Firefox, Safari, etc.')
    
    screenshot_ids = fields.Many2many('ir.attachment', 
                                     'error_report_attachment_rel',
                                     'error_id', 'attachment_id',
                                     string='Screenshots/Attachments',
                                     help='Upload screenshots or error logs')
    
    fix_notes = fields.Html(string='Fix Notes', tracking=True,
                           help='Notes about how this was fixed')
    
    fix_commit = fields.Char(string='Git Commit', tracking=True,
                            help='Git commit hash where this was fixed')
    
    fixed_date = fields.Datetime(string='Fixed Date', tracking=True,
                                help='When this error was fixed')
    
    assigned_to = fields.Many2one('res.users', string='Assigned To',
                                 tracking=True, help='Who is fixing this error?')
    
    related_errors = fields.Char(string='Related Errors',
                                help='Links to similar or related error reports')
    
    color = fields.Integer(string='Color Index', compute='_compute_color', store=True)

    @api.depends('status', 'impact')
    def _compute_color(self):
        """Set color based on status and impact for kanban view"""
        for record in self:
            if record.status == 'fixed':
                record.color = 10  # Green
            elif record.status == 'wont_fix':
                record.color = 7   # Gray
            elif record.impact == 'critical':
                record.color = 1   # Red
            elif record.impact == 'high':
                record.color = 3   # Orange
            else:
                record.color = 0   # White

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate name if not provided"""
        for vals in vals_list:
            if not vals.get('name'):
                reporter = self.env['res.users'].browse(vals.get('reporter_id', self.env.uid))
                vals['name'] = f"Error by {reporter.name} - {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return super().create(vals_list)

    def action_mark_fixed(self):
        """Quick action to mark as fixed"""
        self.write({
            'status': 'fixed',
            'fixed_date': fields.Datetime.now(),
        })

    def action_mark_in_progress(self):
        """Quick action to mark as in progress"""
        self.write({'status': 'in_progress'})

