from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import os


from django.contrib.auth import get_user_model
User = get_user_model()


from .constants import AVATAR_SIZE, AVATAR_COLORS




def create_avatar(display_name, username):
        msg = str(display_name)[0].upper()
        W, H = AVATAR_SIZE
        color = random.choice(AVATAR_COLORS)
        fill_color = color[0]
        font_color = color[2]

        img = Image.new("RGB", (W, H), fill_color)

        # get font
        font_path = os.path.join(settings.BASE_DIR, 'core/custom_moduls/fonts', 'arial.ttf')
        font = ImageFont.truetype(font_path, size=100)

        # fraw letter on image
        draw = ImageDraw.Draw(img)
        draw.text((W / 2, H / 2), msg, font=font, anchor='mm', fill=font_color)

        # convert pil img to InMemoryUploadedFile
        bytes_io = BytesIO()
        img.save(bytes_io, format='JPEG')
        file = InMemoryUploadedFile(
            bytes_io,                    # file
            None,                        # field_name
            username+'.webp',            # file name
            'image/webp',                # content_type
            bytes_io.getbuffer().nbytes, # size
            None                         # content_type_extra
        )

        return file


