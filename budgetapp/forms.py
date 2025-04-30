from django import forms
from .models import Transaction, Category, Subcategory

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'subcategory', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
