from django import newforms as forms

class GameCreateForm(forms.Form):
    name = forms.CharField(max_length=100)
    num_players = forms.ChoiceField(choices=[(2,2), (3,3), (4,4)])
    p1 = forms.CharField(max_length=20)
    p2 = forms.CharField(max_length=20)
    p3 = forms.CharField(max_length=20)
    p4 = forms.CharField(max_length=20)
