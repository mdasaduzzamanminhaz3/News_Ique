from django.shortcuts import redirect
def api_root_views(request):
    return redirect('api-root')