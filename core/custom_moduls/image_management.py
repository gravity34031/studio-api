import os, shutil
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


def deleteFolder(path):
    err = {'error': 'Ошибка при удалении изображений'}
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return err
    except OSError as e:
        return err
    return None

def deleteTitleFolder(instance):
    imgs_folder = os.path.join(settings.MEDIA_ROOT, instance.img_path, instance.slug)
    error = deleteFolder(imgs_folder)
    return error if error else None # response http_400_bad_request

def deleteFramesFolder(frames_path):
    path = os.path.join(settings.MEDIA_ROOT, frames_path)
    error = deleteFolder(path)
    return error if error else None # response http_400_bad_request



def deleteImgAndThumb(image, thumbnail):
    err = None
    for img in (image, thumbnail):
        error = deleteImage(img)
        if error:
            err = error
    error = err
    return error if error else None # response http_400_bad_request

def deleteImage(image):
    img_path = os.path.join(settings.MEDIA_ROOT, str(image))
    err = {'error': 'Ошибка при удалении изображения'}
    try:
        if os.path.isfile(img_path):
            os.remove(img_path)
        else:
            return err
    except OSError as e:
        return err
    return None