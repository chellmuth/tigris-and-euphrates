from django import newforms as forms

class GameCreateForm(forms.Form):
    name = forms.CharField(max_length=100)

