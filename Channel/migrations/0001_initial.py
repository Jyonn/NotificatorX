from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('Account', '0002_alter_account_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelDeliveryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(db_index=True, max_length=36)),
                ('channel', models.CharField(max_length=32)),
                ('message', models.TextField()),
                ('delivery', models.TextField()),
                ('request_time', models.DateTimeField(auto_now_add=True)),
                ('finish_time', models.DateTimeField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error', models.TextField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_delivery_logs', to='Account.account')),
            ],
            options={
                'db_table': 'Channel_delivery_log',
            },
        ),
    ]
