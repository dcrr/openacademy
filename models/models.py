# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")

    # CHECK that the course description and the course title are different
    # Make the Course's name UNIQUE (name, sql_definition, message)
    _sql_constraints = [('name_description_check', 'CHECK(name != description)',
                         "The title of the course should not be the description"),
                        ('name_unique', 'UNIQUE(name)', "The course title must be unique"),
                        ]

    @api.multi
    def copy(self, default=None):
        """ Re-implement your own "copy" method which allows to duplicate the Course object,
            changing the original name into "Copy of [original name]"."""
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)


class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    # the default value can be a python literal value (boolean, integer, float, string)
    # or a function that returns value
    start_date = fields.Date(default=fields.Date.today)
    # (6,2) indicates the accuracy of the number
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=[('instructor','=',True),
                                                                            ('category_id.name','ilike', "Teacher")])
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken Seats", compute='_taken_seats')

    # specifies the fields on which the taken_seats fields depends to be calculated
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        """Calculate the value of the taken_seats field
           Returns the value of taken_seats field"""
        # the object self is a recordset, that is, an ordered collection of records
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0*len(r.attendee_ids)/r.seats

    # specifies the fields, which when changed, triggers the event _verify_valid_seats
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        """Checks if the seats numbers is negative or less than the numbers of attendees
           and generates an warn"""
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

    # specifies which fields are involved in the constraint
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        """Checks that the instructor is not present in the attendees"""
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")