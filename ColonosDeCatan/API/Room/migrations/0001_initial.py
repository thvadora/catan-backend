# Generated by Django 2.2.6 on 2019-11-21 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('PlayerInfo', '0001_initial'),
        ('Board', '0001_initial'),
        ('Games', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('max_players', models.IntegerField(default=4)),
                ('game_has_started', models.BooleanField(default=False)),
                ('board', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='board', to='Board.Board')),
                ('game', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Games.Game')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='own', to=settings.AUTH_USER_MODEL)),
                ('players', models.ManyToManyField(to='PlayerInfo.Player')),
            ],
        ),
    ]