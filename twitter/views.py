from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Tweet, Comment
from .forms import TweetForm, SignUpForm, ProfilePicForm, UpdateUserForm, CommentForm


def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, ("Your Tweet Has Been Posted!"))
                return redirect('home')
            
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets, "form": form})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles": profiles})
    else:
        messages.success(request, ("You must be logged in to view this page..."))
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        messages.success(request, (f"You Have Successfully Unfollowed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, (f"You Have Successfully Followed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        tweets = Tweet.objects.filter(user_id=pk).order_by("-created_at")

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']

            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)

            current_user_profile.save()
            
        return render(request, "profile.html", {"profile": profile, "tweets": tweets})
    else:
        messages.success(request, ("You must be logged in to view this page..."))
        return redirect('home')


def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {"profiles": profiles})
        else:
            messages.success(request, ("That's Not Your Profile Page..."))
            return redirect('home')
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {"profiles": profiles})
        else:
            messages.success(request, ("That's Not Your Profile Page..."))
            return redirect('home')
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, ("You Have Been Logged In! Start Tweeting!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error logging in. Please Try Again..."))
            return redirect('login')
    return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, ("Saindo..."))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have successfully registered! Welcome!"))
            return redirect('home')

    return render(request, "register.html", {'form': form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = request.user
        profile_user = Profile.objects.get(user=current_user)

        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, ("Seu Usuário foi atualizado"))
            return redirect('home')

        return render(request, "update_user.html", {
            'user_form': user_form,
            'profile_form': profile_form
        })

    messages.success(request, ("Precisa estar logado..."))
    return redirect('home')


def tweet_like(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)
        if tweet.likes.filter(id=request.user.id):
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)

        return redirect(request.META.get("HTTP_REFERER"))

    messages.success(request, ("Precisa estar logado..."))
    return redirect('home')


def delete_tweet(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)

        if request.user == tweet.user:
            tweet.delete()
            messages.success(request, ("Deletado!"))
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("Não é seu Tweet!!"))
            return redirect('home')

    messages.success(request, ("Precisa estar logado..."))
    return redirect('home')


def edit_tweet(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)

        if request.user == tweet.user:
            form = TweetForm(request.POST or None, instance=tweet)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request, ("Foi atualizado!"))
                    return redirect('home')

            return render(request, "edit_tweet.html", {'form': form, 'tweet': tweet})

        messages.success(request, ("Não é seu Tweet!!"))
        return redirect('home')

    messages.success(request, ("Precisa estar logado..."))
    return redirect('home')

def comment_tweet(request, pk):
    tweet = get_object_or_404(Tweet, id=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            return redirect('home')  # ou redirect da página que desejar
    return redirect('home')
