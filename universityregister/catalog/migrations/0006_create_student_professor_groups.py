from django.db import migrations

STUDENT_GROUP_NAME = 'Students'
PROFESSOR_GROUP_NAME = 'Professors'


def create_role_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=STUDENT_GROUP_NAME)
    Group.objects.get_or_create(name=PROFESSOR_GROUP_NAME)


def remove_role_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=[STUDENT_GROUP_NAME, PROFESSOR_GROUP_NAME]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_classgroup_status'),
    ]

    operations = [
        migrations.RunPython(create_role_groups, remove_role_groups),
    ]
