from core.models import Frame
# from core.serializers import FrameSerializer

def create_frames(title, frames):
    if title and len(frames) > 0:
        bulk = []
        for frame in frames:
            image = frame
            image_thumbnail = frame
            bulk.append(Frame(title=title, image=image, image_thumbnail=image_thumbnail))
        Frame.objects.bulk_create(bulk)
            # frame_data = {'image': frame, 'title': title}
            # frame_serializer = FrameSerializer(data=frame_data) #type: ignore
            # frame_serializer.is_valid(raise_exception=True)
            # frame_serializer.save()

def pop_frames_from_data(data):
    if data and type(data) is not dict: # protect if there's no data in request
        ## avoid change querydict error
        data._mutable = True
        frames = data.pop('frames', [])
        data._mutable = False
        ##
        return data, frames
    return data, []

def get_client_ip(request):
    # client ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if haven't ip
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    # get server ip
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip