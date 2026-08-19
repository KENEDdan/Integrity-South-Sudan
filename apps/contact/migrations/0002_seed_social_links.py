from django.db import migrations


SOCIAL_LINKS = {
    "facebook_url": "https://www.facebook.com/profile.php?id=100063596655491",
    "twitter_url": "https://x.com/IntegritySouth",
    "youtube_url": "https://youtube.com/@integritysouthsudan?si=Dqw9DdE1vbgWawe2",
}


def seed_social_links(apps, schema_editor):
    ContactInfo = apps.get_model("contact", "ContactInfo")
    obj, _ = ContactInfo.objects.get_or_create(pk=1)
    for field, value in SOCIAL_LINKS.items():
        setattr(obj, field, value)
    obj.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("contact", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_social_links, noop),
    ]
