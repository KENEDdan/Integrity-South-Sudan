from django.db import models


class AboutUs(models.Model):
    executive_summary = models.TextField(default=(
        "Integrity South Sudan is a dynamic civil society organization dedicated to promoting "
        "democracy, good governance, transparency, accountability and peacebuilding in South Sudan. "
        "Formed in 2017 by a group of ambitious South Sudanese professionals and officially registered "
        "with the Relief and Rehabilitation Commission (RRC) in 2023, ISS has established itself as a "
        "credible and influential voice in the country's governance and anti-corruption landscape.\n\n"
        "With operational presence in Central Equatoria and Western Equatoria States and plans for "
        "expansion to the rest of the states, ISS works at the intersection of governance, media "
        "advocacy, protection, livelihood and peacebuilding. Through strategic partnerships with UNMISS, "
        "the World Bank, Friedrich-Ebert-Stiftung (FES) and the European Union, the organization has "
        "successfully implemented initiatives that empower citizens — particularly youth and women — to "
        "actively participate in democratic processes and hold leaders accountable."
    ))
    vision = models.TextField(default=(
        "A world free from poverty and the promotion of a healthy and hunger-free society."
    ))
    mission = models.TextField(default=(
        "To eradicate poverty, illiteracy and diseases affecting our communities in South Sudan, "
        "Integrity South Sudan (ISS) uses its means and commitment to empower local communities to "
        "overcome the root causes of poverty, illiteracy and disease. As agriculture is the backbone "
        "of South Sudan's economy and a quick means of raising wealth for our people, ISS supports "
        "community-level activities that improve standards of living — including training in improved "
        "health and agricultural practices, and financial assistance for grassroots agricultural activities."
    ))
    core_values = models.TextField(default=(
        "Integrity — We believe in honesty and strong moral uprightness, consistently upholding ethical "
        "standards throughout our work with communities.\n\n"
        "Transparency — We operate in an open manner, ensuring our actions, decisions and processes are "
        "visible and accessible to all stakeholders.\n\n"
        "Accountability — We are answerable to our stakeholders, acknowledging and assuming responsibility "
        "for our actions, services and decisions.\n\n"
        "Diversity — We embrace generational, cultural, sexual and gender diversity, recognizing that "
        "different perspectives generate innovative ideas and mutual learning based on equality and "
        "non-discrimination.\n\n"
        "Innovation — We ensure technological advances are effectively and responsibly used to transform "
        "lives for the better, while mitigating potential harms."
    ))
    thematic_areas = models.TextField(default=(
        "Democracy & Good Governance — Strengthening democratic institutions, advocating for transparent "
        "and accountable governance, promoting citizen participation in decision-making, and monitoring "
        "electoral processes.\n\n"
        "Livelihood — Supporting agricultural activities at community level, training communities in "
        "improving agricultural potential, and promoting food security and sustainable livelihoods.\n\n"
        "Environmental Protection & Climate Change — Promoting sustainable environmental practices, "
        "building community resilience to climate impacts, and supporting climate-smart agriculture.\n\n"
        "Media Advocacy — Using media platforms to sensitize communities on democratic processes, fighting "
        "corruption through demand for accountability, and producing civic education content.\n\n"
        "Protection & Gender-Based Violence — Strengthening community mechanisms to protect human rights, "
        "preventing and mitigating GBV risks, and promoting the rights of women, girls and marginalized "
        "groups.\n\n"
        "Peace and Security — Fostering social cohesion and reconciliation, preventing and resolving "
        "conflict through dialogue, and supporting early warning and early response mechanisms."
    ))
    strategic_objectives = models.TextField(default=(
        "1. Strengthen and advocate for good governance systems that guarantee lasting peace, "
        "transparency, accountability, human rights, security, justice and equality in South Sudan.\n\n"
        "2. Empower communities to overcome poverty, illiteracy and disease through sustainable "
        "livelihood programs, agriculture support and health interventions.\n\n"
        "3. Promote environmental sustainability and climate resilience through advocacy, training and "
        "community-based interventions.\n\n"
        "4. Promote the use of media in sensitizing communities on democratic processes and fighting "
        "corruption through demand for accountability and transparency in the use of public resources.\n\n"
        "5. Strengthen community mechanisms to protect human rights and prevent and mitigate GBV risks "
        "through enhanced preparedness and resilience.\n\n"
        "6. Foster lasting peace and security through dialogue, reconciliation and conflict prevention."
    ))
    key_achievements_summary = models.TextField(blank=True, default=(
        "ISS has worked with UNMISS and the World Bank to strengthen Public Financial Management in "
        "government institutions at national and state level; hosted the \"Integrity Hour\" radio program "
        "on Advance Youth Radio 99.9 Juba to restore citizen trust in public service delivery; secured "
        "approval from the Central Equatoria State Ministry of Education to establish Integrity Clubs in "
        "secondary schools and universities; and, through the Raising Civil Voices project with BANAT "
        "Power Initiative, FES and the EU, delivered community dialogue forums and a national policy "
        "roundtable on the South Sudan National Youth Development Policy (2025)."
    ))
    leadership_note = models.CharField(
        max_length=200, default="Led by Chief Executive Director Luate Satimon Joel.",
    )
    partners_note = models.TextField(blank=True, default=(
        "ISS works through strategic partnerships with UNMISS, the World Bank, Friedrich-Ebert-Stiftung "
        "(FES), the European Union, and the BANAT Power Initiative."
    ))
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "About Us Content"