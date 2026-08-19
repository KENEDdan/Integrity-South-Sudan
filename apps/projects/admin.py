from django.contrib import admin
from .models import (
    Donor, Project, BeneficiaryRecord, MEIndicator, FieldReport, Issue, ProjectTask, ProjectDocument,
)

admin.site.register(Donor)
admin.site.register(Project)
admin.site.register(BeneficiaryRecord)
admin.site.register(MEIndicator)
admin.site.register(FieldReport)
admin.site.register(Issue)
admin.site.register(ProjectTask)
admin.site.register(ProjectDocument)