from django.shortcuts import render,redirect

# Create your views here.
def index(request):
    name = 'Banco da Saúde'
    args = {'myName': name}
    if request.user.is_authenticated:
        return redirect('medicamentos:begin_order') 
    else:
        return render(request, 'index.html', args)