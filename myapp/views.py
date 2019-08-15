from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import NameForm


# Create your views here.
def index(request):
    name = 'World'
    return render(request, 'myapp/index.html', {'name': name})


def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            return HttpResponseRedirect(reverse('myapp:index'), content={'name': name})
    else:
        form = NameForm()
    return render(request, 'myapp/name.html', {'form': form})
