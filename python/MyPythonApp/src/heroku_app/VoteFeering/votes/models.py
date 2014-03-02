# coding: utf8

from django.db import models
from django.forms import ModelForm
import datetime
from django.utils import timezone
from django.contrib import admin

# Create your models here.
class Vote(models.Model):
    image_fname = models.CharField(max_length=200)
    vote_hand = models.IntegerField() #
    vote_tip = models.IntegerField() #
    total_vote = models.IntegerField() #
    hand_flag = models.IntegerField() #
    
    def __unicode__(self):
        return self.image_fname, self.vote_hand, self.vote_tip, self.total_vote 
 
class VoteForm(ModelForm):
    class Meta:
        model = Vote
        fields = ('')

admin.site.register(Vote)
