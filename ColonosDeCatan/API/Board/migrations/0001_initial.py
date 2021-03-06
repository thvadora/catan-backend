# Generated by Django 2.2.6 on 2019-11-21 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='HexPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('index', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='VertexPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('index', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='RoadPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='x', to='Board.VertexPosition')),
                ('y', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='y', to='Board.VertexPosition')),
            ],
        ),
        migrations.CreateModel(
            name='Hex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.IntegerField()),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='position', to='Board.HexPosition')),
                ('roads', models.ManyToManyField(related_name='hex_roads', to='Board.RoadPosition')),
                ('terrain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource', to='Board.Resource')),
                ('vertexes', models.ManyToManyField(related_name='hex_vertexes', to='Board.VertexPosition')),
            ],
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('hexes', models.ManyToManyField(to='Board.Hex')),
            ],
        ),
    ]
