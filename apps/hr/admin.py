from django.contrib import admin
from .models import (
    Staff, LeaveRequest, TimesheetRecord, JobOpening, Applicant,
    TrainingRecord, StaffDocument, PayrollRun, PolicyDocument,
)

admin.site.register(Staff)
admin.site.register(LeaveRequest)
admin.site.register(TimesheetRecord)
admin.site.register(JobOpening)
admin.site.register(Applicant)
admin.site.register(TrainingRecord)
admin.site.register(StaffDocument)
admin.site.register(PayrollRun)
admin.site.register(PolicyDocument)