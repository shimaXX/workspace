# coding: utf8
# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render
from votes.models import *
from django.template import RequestContext 
from django.template.loader import get_template
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect

def votefeeling(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            image = request.POST['imname']
            if 'v1' in request.POST:
                obj = Vote.objects.get(image_fname = image)
                num_vote = obj.vote_hand + 1
                t_vote = obj.total_vote + 1
                if num_vote > obj.vote_tip: flag=1
                elif num_vote == obj.vote_tip: flag=0
                else: flag=2
                Vote.objects.filter(image_fname = image).update(vote_hand = num_vote, total_vote = t_vote, hand_flag=flag)
            elif 'v2' in request.POST:
                obj = Vote.objects.get(image_fname = image)
                num_vote = obj.vote_tip + 1
                t_vote = obj.total_vote + 1
                if num_vote > obj.vote_hand: flag=2
                elif num_vote == obj.vote_tip: flag=0
                else: flag=1
                Vote.objects.filter(image_fname = image).update(vote_tip = num_vote, total_vote = t_vote, hand_flag=flag)
        form = VoteForm()
        imname = calculate_num_votes()
        return render_to_response('votefeeling.html',
                        {
                            'form1':form,
                            'imname':imname
                        },
                    context_instance=RequestContext(request)
                )
    else:
        form = VoteForm()
        imname = calculate_num_votes()   
        return render_to_response('votefeeling.html',
                        {
                            'form1':form,
                            'imname':imname
                        },
                    context_instance=RequestContext(request)
                )

def calculate_num_votes():
    votes = Vote.objects.filter(image_fname__contains = '')
    fname = { c.image_fname:c.total_vote for c in votes }
    imname = [ k for k,v in sorted(fname.items(), key=lambda x:x[1]) ][0]
    return imname


def index(request):
    return render_to_response('index.html', {},
            context_instance=RequestContext(request))

def login(request):
    user_id = request.POST['user_id']
    password = request.POST['password']
    user = authenticate(username=user_id, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return redirect('/votehome/')
        else:
            return redirect('/')
    else:
        return redirect('/')

def home(request):
    return render_to_response('home.html', {})
