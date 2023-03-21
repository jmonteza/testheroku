from django import forms
from .models import *

class SignupForm(forms.Form):
    display_name = forms.CharField(label='Display Name', max_length=50, required=True)
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    github = forms.CharField(label='GitHub Username', required=False)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput, required=True)

class SigninForm(forms.Form):
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'content', 'content_type', 'visibility','receivers', 'unlisted', 'image' )

        widget = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'description' : forms.TextInput(attrs={'class': 'form-control'}),
            'content' : forms.Textarea(attrs={'class': 'form-control'}),
            'content_type' : forms.Select(attrs={'class': 'form-control'}),
            'visibility' : forms.TextInput(attrs={'class': 'form-control'}),
            'receivers' : forms.SelectMultiple(attrs={'class': 'form-control'}),
            'unlisted' : forms.TextInput(attrs={'class': 'form-control'}),
            'image' : forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, user,receiver_list = None,commit=True):
        print('save method called')
        post = super().save(commit=False)
        post.made_by = user
        if commit:
            post.save()
            if receiver_list:
                for receiver_id in receiver_list:
                    author = Author.objects.get(id=receiver_id)
                    post.receivers.add(author)

        return post

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['receiver'].widget.attrs.update({'class': 'form-control'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)

        widgets = {
            'comment' : forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, user, post,commit=True):
        print('save method called')
        comment = super().save(commit=False)
        comment.author = user
        comment.post = post
        if commit:
            comment.save()

        return comment