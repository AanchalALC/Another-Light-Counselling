from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0023_auto_20260915_1433"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contactdetails",
            options={
                "ordering": (
                    models.Case(
                        models.When(key="instagram", then=models.Value(0)),
                        models.When(key="facebook", then=models.Value(1)),
                        models.When(key="whatsapp", then=models.Value(2)),
                        models.When(key="linkedin", then=models.Value(3)),
                        models.When(key="youtube", then=models.Value(4)),
                        models.When(key="phone", then=models.Value(5)),
                        models.When(key="email", then=models.Value(6)),
                        models.When(
                            key__in=("address", "physical_address", "location"),
                            then=models.Value(7),
                        ),
                        default=models.Value(8),
                        output_field=models.IntegerField(),
                    ),
                    "id",
                ),
                "verbose_name": "Another Light Contact Detail",
                "verbose_name_plural": "Another Light Contact Details",
            },
        ),
    ]
