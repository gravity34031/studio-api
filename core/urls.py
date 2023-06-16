from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .views import *
from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
router.register(r'studio', StudioViewSet, basename='studio')
router.register(r'actor', ActorViewSet, basename='actor')
router.register(r'genre', GenreViewSet, basename='genre')

router.register(r'schedule', ScheduleViewSet, basename='schedule') # get schedule including title on it
"""
    GET: title is an instance of the model
    POST: title in request is a SLUG. Ex: {'title': 'Vinland saga'}
"""



#urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path('titles/', TitleListView.as_view()), # get, post. Get returns common base (sorting by title name Az) ('Релизы')
    path('titles/<slug:slug>/', TitleRetrieveView.as_view()), #get, patch, delete
    path('random-title/', RandomTitleView.as_view()),
    path('frame/', FramePostView.as_view()), # create Frame
    path('frame/<int:pk>/', FrameDeleteView.as_view()), # delete Frame by id
    path('frames/<slug:slug>/', FramesDeleteView.as_view()), # delete all Frames by post slug

    path('genre-title/<slug:slug>/', TitleByGenreView.as_view()), # get all titles related to genre. <slug> of the genre
    path('studio-title/<slug:slug>/', TitleByStudioView.as_view()), # get all titles related to studio. <slug> of the studio
    path('actor-title/<slug:slug>/', TitleByActorView.as_view()), # get all titles related to actor. <slug> of the actor

    path('rating/', RatingListView.as_view()), # get, patch. Get returns all titles sorted by rating. Patch for create and update!
    path('rating/<slug:slug>/', RatingDeleteView().as_view()), # delete. <slug> is a title slug

    path('favourite/<slug:slug>/', FavouriteView.as_view()), # patch to post and delete favourite. <slug> of the title
]


"""
---TITLE---
    This fields is required:
        "title"
        "slug":
        "poster"
        "description"
        "aired_on"
        "episodes"
        "episodes_aired"
        "author":
    This fields is generating automaticly:
        "poster_thumbnail"
        "author"
        "create_time"
        "update_time"
    This fields is a LIST of the slugs or just a slug:
        "studios"
        "actors"
        "genres" 
    "alternative_title" must be a STRING. If sent NULL in patch alt_titles will be deleted. Separator is ';'. data: {
        'alternative_title': 'Атака титанов; Attack on titan'
    } result: 1) Атака титанов 2) Attack on titan
    (
        "frames" can be in post request. This field is ignoring in PATCH request. 
        After creating title it can be added using POST request to <frame/> endpoint
    )
    "schedule" is filling by hands after title was created:


    "auto_related_list" may be included to request. if true, related_list will created automaticly. 
                                                    field "related_lists" will be ignored
                        in PATCH it will ADD related_titles to already exist


    "related_lists" in PATCH will DELETE exist related_titles and CREATE new
                    it is a String consisting slugs. Separator ';'. 
                    e.g.: "related_lists": "Атака титанов;   Мэшл   ;" = ['Атака титанов', 'Мэшл']


    This fields is a count of the objects in related table:
        "views"
        "favourites"
"""


"""
TITLE PARAMS:
    ordering: .../titles/?ordering=aired_on sorting by fields: ('create_time', 'update_time', 'title', 'aired_on', 'rating', 'popular'). Create time is default
    search: .../titles/?search=doctor_stone
    filters: look down

    SEARCH is performed by: 'title', 'alternative_title', 'slug' AND related titles

    Params can be combined. e.g.: .../titles/?ordering=title&search=атака титанов


TITLE FILTERS:
    rating - titles with minimal average rating: rating_gte=6 fits: (6, 7,... 10) not fits: (1, 2,... 5)

    aired_on_from
    aired_on_to

    genres      filtering by models that have ManyToMany. It is SLUG's of the models.
    actors      Params can include multiple values. 
    studios     e.g: .../titles/?genres=hunter-x-hunter&genres=death-note

    status      Онгоин/Вышел
"""




"""
---FRAME---
    "title"
    "image

"""