from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz


def action_workflow(self, model_group):
    next_group_users = self.env.ref(model_group).users
    list_group_users = []
    for user in next_group_users:
        list_group_users.append(user.name)
    string_group_users = ', '.join(list_group_users)
    user_tz = pytz.timezone(self.env.context.get('tz') or self.env.tz)
    self.env['appointment.workflow'].create({
        'action_id': self.id,
        'action_name': self.state.capitalize(),
        'date': datetime.now(tz=user_tz).strftime("%d/%m/%Y %H:%M:%S"),
        'user': self.env.user.name,
        'next_action': string_group_users
    })


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _order = "doctor_id, gender, age"

    name = fields.Char(string='Order reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    age = fields.Integer(string='Age', tracking=True, related='patient_id.age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], String='Gender', readonly=True, related='patient_id.gender')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', string='Status',
                             tracking=True)
    note = fields.Text(string='Description', readonly=True)
    date_appointment = fields.Date(string='Date')
    date_checkup = fields.Datetime(string='Check Up Time')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    prescription = fields.Text(string='Prescription')
    prescription_line_ids = fields.One2many('appointment.prescription.lines', 'appointment_id',
                                            string='Prescription Lines')
    workflow_ids = fields.One2many('appointment.workflow', 'action_id', string='Workflow')

    def action_confirm(self):
        self.state = 'confirm'
        action_workflow(self, 'om_hospital.group_patient_done')


    def action_done(self):
        self.state = 'done'
        action_workflow(self, 'om_hospital.group_patient_cancel')

    def action_draft(self):
        self.state = 'draft'
        action_workflow(self, 'om_hospital.group_patient_confirmed')

    def action_cancel(self):
        self.state = 'cancel'
        action_workflow(self, 'om_hospital.group_patient_draft')


    def date_created(self):
        user_id=pytz.timezone(self.env.context.get('tz') or self.env.tz)
        return str(datetime.now(tz=user_id).strftime(("%d/%m/%Y %H:%M:%S")))

    def next_workflow_action(self, model_group):
        next_group_users = self.env.ref(model_group).users
        list_group_users = []
        for user in next_group_users:
            list_group_users.append(user.name)
        string_group_users = ', '.join(list_group_users)
        return string_group_users


    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Patient'
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        res = super(HospitalAppointment, self).create(vals)
        return res

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.gender = ''
            self.note = ''

    def unlink(self):
        if self.state == 'done' or self.state == 'cancel':
            raise ValidationError(_("You cannot delete %s as it is in done state" % self.name))
        return super(HospitalAppointment, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://www.google.com',
        }


class AppointmentPrescriptionLines(models.Model):
    _name = "appointment.prescription.lines"
    _description = "Appointment Prescription Lines"

    name = fields.Char(string="Medicine", required=True)
    qty = fields.Integer(string="Quantity")
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')


class AppointmentWorkflow(models.Model):
    _name = "appointment.workflow"
    _description = "Appointment Workflow"

    action_id = fields.Many2one('hospital.appointment', string="Action")
    action_name = fields.Char(string="Action")
    user = fields.Char(string="User")
    date = fields.Char(string="Date")
    next_action = fields.Char(string="Next Workflow")



    @api.model
    def default_get(self, fields):
        result = super(AppointmentWorkflow, self).default_get(fields)
        print(self._context)
        result['action_name'] = 'salam'
        return result
