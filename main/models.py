from django.db import models

class User(models.Model):   
    id = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=10)
    email = models.CharField(unique=True, max_length=30)
    belong = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'User'


class Project(models.Model):
    title = models.CharField(max_length=20)
    team = models.CharField(max_length=10)
    description = models.TextField()
    subject = models.CharField(max_length=20, blank=True, null=True)
    purpose = models.CharField(max_length=30, blank=True, null=True)
    progress_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Project'


class Member(models.Model):
    project = models.ForeignKey('Project', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    leader = models.IntegerField(blank=True, null=True)
    contribution_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Member'
        unique_together = (('project_id', 'user_id'),)


class Notification(models.Model):
    project = models.ForeignKey('Project', models.DO_NOTHING)
    invitee = models.ForeignKey('User', models.DO_NOTHING, db_column='invitee', related_name='invitee')
    inviter = models.ForeignKey('User', models.DO_NOTHING, db_column='inviter', related_name='inviter')
    invite_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Notification'
        unique_together = (('project_id', 'invitee'),)


class Schedule(models.Model):
    project = models.ForeignKey(Project, models.DO_NOTHING)
    writer = models.ForeignKey('User', models.DO_NOTHING, db_column='writer')
    title = models.CharField(max_length=20)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Schedule'


class File(models.Model):
    project = models.ForeignKey('Project', models.DO_NOTHING)
    writer = models.ForeignKey('User', models.DO_NOTHING, db_column='writer')
    title = models.CharField(max_length=20)
    description = models.TextField()
    file_name = models.CharField(max_length=20)
    file_url = models.CharField(max_length=100)
    create_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'File'


class Todo(models.Model):
    project = models.ForeignKey(Project, models.DO_NOTHING)
    writer = models.ForeignKey('User', models.DO_NOTHING, db_column='writer')
    title = models.CharField(max_length=20)
    description = models.TextField()
    state = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Todo'


class Participant(models.Model):
    todo = models.OneToOneField('Todo', models.DO_NOTHING, primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Participant'
        unique_together = (('todo_id', 'user_id'),)


class Comment(models.Model):
    todo = models.ForeignKey('Todo', models.DO_NOTHING)
    writer = models.ForeignKey('User', models.DO_NOTHING, db_column='writer')
    content = models.TextField()
    create_at = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Comment'
