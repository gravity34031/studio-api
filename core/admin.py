from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    pass


@admin.register(TitleRating)
class TitleRatingAdmin(admin.ModelAdmin):
    pass


@admin.register(Schedule)
class ScheduleParentsAdmin(admin.ModelAdmin):
    pass


###
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    pass


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    pass


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    pass
###



@admin.register(TitleViews)
class ViewsAdmin(admin.ModelAdmin):
    pass







# @admin.register(RelatedTitles)
# class RelatedTitlesAdmin(admin.ModelAdmin):
#     pass







