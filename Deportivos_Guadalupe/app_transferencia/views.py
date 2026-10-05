from django.shortcuts import render

# Create your views here.
def fn_getpost_rider(request):
    resultado = ""
    dato = None
    metodo = request.method
    
    if request.method == 'GET':
        dato = request.GET.get("dato")
        if dato:
            resultado = "El dato llegó mediante GET."

    elif request.method == "POST":
        dato = request.POST.get("dato")
        if dato:
            resultado = "El dato llegó mediante POST"

    return render(
        request, "app_transferencia/index.html",
        {
            "resultado": resultado,
            "dato": dato,
            "metodo": metodo,
        }
    )