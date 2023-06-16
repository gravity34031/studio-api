import os
from pytils import translit
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# RESERVED_URLS = (
#         'actor',
#         'studio',
#         'genre'
#     )
# def validate_title_slug(slug): # title slug must not to be like reserved urls (studio, actor, genre)
#     if slug in RESERVED_URLS:
#         raise ValidationError(_('Поле slug не должно быть равно зарезервированному: %(urls)s'), params={'urls': RESERVED_URLS})


def get_img_path(self, filename, thumbnail=False): # dynamic upload_file
    img_path = self.img_path # path to img folder
    # extension = filename.split('.')[-1]
    # name = '.'.join(list(filename.split('.')[:-1]))
    # name = str(translit.slugify(name))
    # filename = f'{name}.{extension}'

    class_name = type(self).__name__
    if class_name == 'Title':
        if not thumbnail:
            img_path = self.poster_path
        else:
            img_path = self.poster_thumbnail_path
    else:
        if thumbnail:
            img_path = self.img_thumbnail_path
    final_path = os.path.join(img_path, filename)
        # slug = self.__dict__.get('slug', '')
        # final_path = os.path.join(img_path, slug, 'poster/', filename) # if will be changed delete Title will not del imgs
    # elif class_name == 'Frame':
        # frame_title_id = self.__dict__.get('title_id', None)
        # if frame_title_id:
        #     frame_title = get_object_or_404(Title, id=frame_title_id)
        #     slug = frame_title.slug
        #     final_path = os.path.join('title/', slug, 'frames/', filename)
    
    return os.path.join(final_path)



def get_img_thumb_path(self, filename): # recognize if field is a thumbnail not an image
    return get_img_path(self, filename, thumbnail=True)