from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    """
    Category form
    """
    class Meta:
        model = Category
        fields = [
            'name'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        category = super(CategoryForm, self).save(commit=False)
        category.user = self.user
        if commit:
            category.save()
        return category
