from django.db import models
from datetime import datetime

class ChatRoom(models.Model):
    create_date = models.DateTimeField(u'create_time', blank=True, null=True)
    tweet = models.TextField(u'tweet', blank=True)

    def __unicode__(self):
            return self.tweet[:10] + u'...'
