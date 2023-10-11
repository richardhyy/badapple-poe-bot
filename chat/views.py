import json
import os
import time

from decouple import config
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sse_starlette import ServerSentEvent


def require_auth(view_func):
    """
    Decorator to validate access token
    """
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, access_key = auth_header.partition(' ')

        if not config("DEBUG", cast=bool) and (token_type.lower() != 'bearer' or access_key != config("POE_ACCESS_KEY")):
            return JsonResponse({'error': 'Invalid access token'}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


VIDEO_PATH = "resources/" + config("VIDEO_FILENAME", default="bad_apple.txt")

if not os.path.exists(VIDEO_PATH):
    raise FileNotFoundError("Video file not found at " + VIDEO_PATH)


@csrf_exempt
@require_auth
def stream(request):
    def query_event_stream():
        # Send meta event
        yield ServerSentEvent(data=json.dumps(
                {
                    "content_type": "text/markdown",  # For code block rendering
                    "refetch_settings": True,
                    "linkify": True,
                    "suggested_replies": False,
                }
            ), event="meta").encode()

        with open(VIDEO_PATH, 'r') as f:
            ascii_frame = ''
            for line in f:
                if line.strip() == "<END_FRAME>":
                    # If the frame is done, send it to the client
                    time.sleep(1/24)  # Delay a bit
                    yield ServerSentEvent(data=json.dumps({"text": "```badapple_poe\n" + ascii_frame + "```"}), event="replace_response").encode()
                    ascii_frame = ''
                else:
                    ascii_frame += line

        # End response
        yield ServerSentEvent(data="{}", event="done").encode()

    # Handle request
    request = json.loads(request.body)
    request_type = request.get("type")

    # Check request type
    if request_type == "query":
        # Start video stream
        return StreamingHttpResponse(query_event_stream(), content_type="text/event-stream")
    elif request_type == "settings":
        # Return bot settings
        return JsonResponse({
            # This is the first message the bot sends to the user without any input from the user
            "introduction_message": "Say anything to start"
        })
