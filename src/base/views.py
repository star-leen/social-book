from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from itertools import chain
from .models import Profile, Post, LikePost, FollowersCount
import random

User = get_user_model()

# Create your views here.
@login_required(login_url='sign-in')
def index(request):
    user = request.user
    user_profile = Profile.objects.get(user=user)
    
    # following_list = []
    # feed = []
    
    # following = FollowersCount.objects.filter(follower=request.user)
    # for obj in following:
    #     following_list.append(obj.followed)
    
    # for user in following_list:
    #     posts = Post.objects.filter(user=user)
    #     feed.append(posts)
    # posts_qs = list(chain(*feed))
    posts_qs = Post.objects.filter(
        user__in=FollowersCount.objects.filter(follower=request.user).values_list('followed')
        ).order_by("created_at")
    
    # user suggestions:
    all_users = User.objects.all().exclude(username=user.username)
    follow_suggesttions = []
    
    for obj in all_users:
        try:
            check_following = FollowersCount.objects.get(follower=user, followed=obj)
        except FollowersCount.DoesNotExist:
            try:
                profile_of_user = Profile.objects.get(user=obj)
                follow_suggesttions.append(profile_of_user)
            except Profile.DoesNotExist:
                pass
    
    random.shuffle(follow_suggesttions)
    print('follow suggestions: ', follow_suggesttions)
            
    
    # non_followers_count_qs = FollowersCount.objects.all().exclude(follower=user)
    # non_followers = Profile.objects.filter(
    #     user__in=non_followers_count_qs.values_list('followed')
    #     )

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'posts': posts_qs,
        'follow_suggesttions': follow_suggesttions[:3],
    }
    return render(request, 'index.html', context)

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email has already been used')
                return redirect('sign-up')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username has already been used')
                return redirect('sign-up')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                )
                user.save()
                login(request, user)
                
                # user_login = auth.authenticate(username=username, pasword=password1)
                # auth.login(request, user_login)
                user = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user,id_user=user.id)
                new_profile.save()
                
                return redirect('settings')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('sign-up')
        
    else:
        return render(request, 'signup.html', {})
    
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('sign-in')
            
    else:
        return render(request, 'signin.html', {})

@login_required(login_url='sign-in')
def logout(request):
    auth.logout(request)
    return redirect('sign-in')

@login_required(login_url='sign-in')
def settings(request):
    user = request.user
    user_profile = Profile.objects.get(user=user)
    print(user.username)
    
    
    if request.method == 'POST':
        if request.FILES.get('image') is None:
            image = user_profile.profile_img
            bio = request.POST['bio']
            location = request.POST['location']
            
            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            
        elif request.FILES.get('image') is not None:
            image = request.FILES.get('image')
            bio = request.POST.get('bio')
            location = request.POST.get('location')
            
            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('home')
            
    context = {
        'user': user,
        'user_profile': user_profile,
    }
    return render(request, 'settings.html', context)

@login_required(login_url='sign-in')
def upload(request):
    if request.method == 'POST' and request.FILES.get('image_upload') is not None:
        user = request.user
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(
            user = user,
            image = image,
            caption = caption,
        )
        new_post.save()
        return redirect('home')
        

    return redirect('home')

@login_required(login_url='sign-in')
def like_post(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    try:
        get_like_post = LikePost.objects.get(post=post, user=user)
        print('work2')
        get_like_post.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('home')
    
    except LikePost.DoesNotExist: 
        print('work1')
        new_like = LikePost.objects.create(post=post, user=user)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('home')

@login_required(login_url='sign-in')
def profile(request, pk):
    # try:
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_posts = Post.objects.filter(user=user_object)

    viewer = request.user
    profiled_user = User.objects.get(username=pk)
    followers = FollowersCount.objects.filter(followed=profiled_user)
    followers_count = followers.count()
    following = FollowersCount.objects.filter(follower=profiled_user)
    following_count = following.count()

    try:
        fc_obj = FollowersCount.objects.get(follower=viewer, followed=profiled_user)
        button_text = 'Unfollow'

    except FollowersCount.DoesNotExist: 
        button_text = 'Follow'




    # except User.DoesNotExist: 
    #     return redirect('home')
    # except Profile.DoesNotExist: 
    #     return redirect('home')
    # except:
    #     return redirect('home')
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'button_text': button_text,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='sign-in')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        follower = User.objects.get(username=follower)
        followed = request.POST['user']
        followed = User.objects.get(username=followed)

        try:
            fc_obj = FollowersCount.objects.get(follower=follower, followed=followed)
            fc_obj.delete()

        except FollowersCount.DoesNotExist: 
            new_fc_obj = FollowersCount.objects.create(follower=follower, followed=followed)
            new_fc_obj.save()
        return redirect('/profile'+'/'+followed.username)

    else:
        return redirect('home')

@login_required(login_url='sign-in')
def search(request):
    user_profile = Profile.objects.get(user=request.user)
    username = request.GET.get('username') if request.GET.get('username') is not None else ''
    search_qs = Profile.objects.filter(user__username__icontains=username)


    context = {
        'user': request.user,
        'user_profile': user_profile,
        'search_qs': search_qs,
    }
    return render(request, 'search.html', context)