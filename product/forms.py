from django import forms

from product.models import Comment


class SearchForm(forms.Form):

    search_field = forms.CharField()


class CommentForm(forms.ModelForm):

    rating = forms.IntegerField(max_value=5, min_value=0)

    class Meta:
        model = Comment
        fields = ('text', 'rating')
