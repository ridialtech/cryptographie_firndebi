import os
import json
import subprocess
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVEUR_DIR = os.path.join(BASE_DIR, 'serveur')
KEY_DIR = os.path.join(BASE_DIR, 'keys')
PRIVATE_KEY = os.path.join(KEY_DIR, 'private.pem')
PUBLIC_KEY = os.path.join(KEY_DIR, 'public.pem')

os.makedirs(SERVEUR_DIR, exist_ok=True)

@csrf_exempt
def sign_pdf(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    file_obj = request.FILES.get('file')
    if not file_obj:
        return HttpResponseBadRequest('file parameter required')
    filename = os.path.basename(file_obj.name)
    file_path = os.path.join(SERVEUR_DIR, filename)
    with open(file_path, 'wb') as dest:
        for chunk in file_obj.chunks():
            dest.write(chunk)
    sig_path = file_path + '.sig'
    subprocess.run(['openssl', 'dgst', '-sha256', '-sign', PRIVATE_KEY,
                    '-out', sig_path, file_path], check=True)
    return JsonResponse({'message': 'signed', 'file': filename})


def verify_pdf(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    filename = request.GET.get('file')
    if not filename:
        return HttpResponseBadRequest('file parameter required')
    file_path = os.path.join(SERVEUR_DIR, filename)
    sig_path = file_path + '.sig'
    if not os.path.exists(file_path) or not os.path.exists(sig_path):
        return JsonResponse({'error': 'file not found'}, status=404)
    result = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', PUBLIC_KEY,
                             '-signature', sig_path, file_path], stdout=subprocess.PIPE)
    valid = b'Verified OK' in result.stdout
    return JsonResponse({'file': filename, 'valid': valid})
