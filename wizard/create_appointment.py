from odoo import api, fields, models, _


class CreateAppointmentWiz(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment Wizard"

    @api.model
    def default_get(self, fields):
        result = super(CreateAppointmentWiz, self).default_get(fields)
        if self._context.get('active_id'):
            result['patient_id'] = self._context.get('active_id')
        return result


    date_appointment = fields.Date(string='Date')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_name = fields.Many2one('hospital.doctor', string='Doctor', required=True)

    def action_create_appointment(self):
        vals = {
            'patient_id': self.patient_id.id,
            'date_appointment': self.date_appointment,
            'doctor_id': self.doctor_name.id,
        }
        appointment_rec=self.env['hospital.appointment'].create(vals)
        return {
            'name': _('Appointment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hospital.appointment',
            'res_id': appointment_rec.id,
        }
    def action_view_appointment(self):
        action= self.env.ref('om_hospital.action_hospital_appointment').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action