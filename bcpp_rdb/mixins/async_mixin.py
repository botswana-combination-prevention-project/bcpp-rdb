import asyncio
import json
import pytz

from django.conf import settings
from django.http.response import HttpResponse


tz = pytz.timezone(settings.TIME_ZONE)


class AsyncMixin:

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            futures = {}
            task_response_data = {}
            tasks = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            for task_name in self.async_tasks(self.kwargs.get('task_name')):
                futures[task_name] = asyncio.Future()
                tasks.append(self._task(futures[task_name], task_name))
            loop.run_until_complete(asyncio.wait(tasks))
            for task_name, future in futures.items():
                task_response_data[task_name] = future.result()
            loop.close()
            print(task_response_data)
            return HttpResponse(json.dumps(task_response_data), content_type='application/json')
        return self.render_to_response(context)

    @asyncio.coroutine
    def _task(self, future, task_name):
        future.set_result(self.async_task(task_name))

    def async_task(self, name):
        """Override."""
        return {}

    def async_tasks(self, task_name=None):
        """Override."""
        return {}
