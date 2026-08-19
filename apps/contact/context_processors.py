from .models import ContactInfo


def contact_info_processor(request):
    return {"footer_contact": ContactInfo.get_solo()}