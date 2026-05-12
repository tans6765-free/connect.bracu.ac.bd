import os
import traceback
from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin


class VercelExceptionLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if os.environ.get('VERCEL'):
            log_path = '/tmp/vercel_exception.txt'
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('PATH: ' + request.path + '\n')
                    f.write('GET: ' + str(request.GET.dict()) + '\n')
                    f.write('POST: ' + str(request.POST.dict()) + '\n')
                    f.write('EXCEPTION:\n')
                    traceback.print_exc(file=f)
            except Exception:
                pass

            if request.GET.get('debug') == '1':
                tb = traceback.format_exc()
                return HttpResponseServerError(f'<pre>{tb}</pre>')
        return None
