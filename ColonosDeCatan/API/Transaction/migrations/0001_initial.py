# Generated by Django 2.2.6 on 2019-11-21 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Board', '0001_initial'),
        ('PlayerInfo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField()),
                ('player', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='PlayerInfo.Player')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=15, null=True)),
                ('offer', models.ManyToManyField(related_name='offer', to='Board.Resource')),
                ('request', models.ManyToManyField(related_name='request', to='Board.Resource')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to='PlayerInfo.Player')),
                ('responses', models.ManyToManyField(to='Transaction.Response')),
                ('winner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='PlayerInfo.Player')),
            ],
        ),
    ]
