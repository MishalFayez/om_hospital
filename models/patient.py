from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
import datetime
import pytz

from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"
    _order = "id desc"

    @api.model
    def default_get(self, fields):
        result = super(HospitalPatient, self).default_get(fields)
        return result

    name = fields.Char(string='Name', required=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', string='Status',
                             tracking=True)
    resposible_id = fields.Many2one('res.partner', string='Responsible')
    workflow = fields.Text(string='workflow')
    # patientworkflow=fields.One2many('patient.workflow.line','workflow_class',String='Many2one')
    appointment_count = fields.Integer(String='Appointment Count', compute='_compute_appointment_count')
    image = fields.Binary(string='Patient Image')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')



    def _compute_appointment_count(self):
        for rec in self:
            appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])
            rec.appointment_count = appointment_count

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            # rec['workflow']='Mohammed'
            next_group_users = self.env.ref('om_hospital.group_patient_done').users
            list_group_users = []
            for user in next_group_users:
                list_group_users.append(user.name)
            string_group_users = ', '.join(list_group_users)
            tz = pytz.timezone('Asia/Riyadh')
            ct = datetime.datetime.now(tz=tz).strftime("%H:%M")
            self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                                   note=f'Just Confirmed {self.name} at '
                                        f'{str(date.today())} {ct} Please Move Patient to Done State: ' + string_group_users)

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            next_group_users = self.env.ref('om_hospital.group_patient_cancel').users
            list_group_users = []
            for user in next_group_users:
                list_group_users.append(user.name)
            string_group_users = ', '.join(list_group_users)
            tz = pytz.timezone('Asia/Riyadh')
            ct = datetime.datetime.now(tz=tz).strftime("%H:%M")
            self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                                   note=f'Moved {self.name} To Done State at '
                                        f'{str(date.today())} {ct} Cancelation Upon: ' + string_group_users)

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            next_group_users = self.env.ref('om_hospital.group_patient_confirmed').users
            list_group_users = []
            for user in next_group_users:
                list_group_users.append(user.name)
            string_group_users = ', '.join(list_group_users)
            tz = pytz.timezone('Asia/Riyadh')
            ct = datetime.datetime.now(tz=tz).strftime("%H:%M")
            self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                                   note=f'Moved {self.name} To Draft State at '
                                        f'{str(date.today())} {ct} Please Confirm the Patient: ' + string_group_users)

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            next_group_users = self.env.ref('om_hospital.group_patient_draft').users
            list_group_users = []
            for user in next_group_users:
                list_group_users.append(user.name)
            string_group_users = ', '.join(list_group_users)
            tz = pytz.timezone('Asia/Riyadh')
            ct = datetime.datetime.now(tz=tz).strftime("%H:%M")
            self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                                   note=f'Just Cancelled {self.name} at '
                                        f'{str(date.today())} {ct} Draft Upon: ' + string_group_users)

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Patient'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
        res = super(HospitalPatient, self).create(vals)
        next_group_users = self.env.ref('om_hospital.group_patient_confirmed').users
        print(next_group_users)
        list_group_users = []
        for user in next_group_users:
            list_group_users.append(user.name)
        string_group_users = ', '.join(list_group_users)
        tz = pytz.timezone('Asia/Riyadh')
        ct = datetime.datetime.now(tz=tz).strftime("%H:%M")
        self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                               note=f'Moved {self.name} To Draft State at '
                                    f'{str(date.today())} {ct} Please Confirm the Patient: ' + string_group_users)
        print(self.activity_schedule('om.hospital.mail_activity_om_hospital', user_id=self.env.uid,
                                     note=f'Moved {self.name} To Draft State at '
                                          f'{str(date.today())} {ct} Please Confirm the Patient: ' + string_group_users))
        return res


    @api.constrains('name')
    def check_name(self):
        for rec in self:
            patients=self.env['hospital.patient'].search([('name', '=', rec.name), ('id', '!=', rec.id)])
            if patients:
                raise ValidationError(_("name %s already exists" % rec.name))

    @api.constrains('age')
    def check_age(self):
        for rec in self:
            if rec.age == 0:
                raise ValidationError(_("Age cannot be zero"))

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference + ' ' + rec.name
            result.append((rec.id, name))
        return result
    def action_open_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'hospital.appointment',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }