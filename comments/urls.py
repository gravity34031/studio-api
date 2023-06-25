from django.urls import path, include
from .views import *





urlpatterns = [
    path('comment/', CommentView.as_view()), # post comment
    path('comment/<int:pk>/', CommentRetrieveView.as_view()), # patch comment; delete comment

    path('comments/<slug:slug>/', GetCommentsView.as_view()), # get - get all comments for the post. <slug> of the post. must include param content_type

    path('react-comment/<int:pk>/', ReactionCommentView.as_view()), # Patch method. change and delete reaction
]


"""
    GET comments/jujutsu-kaisen/?content_type=(title/news)
    must include param content_type e.g. .../comments/jujutsu-kaisen/?content_type=title

    field your_reaction show YOUR reaction to the comment. 0 - LIKE; 1 - DISLIKE

    Params:
        content_type (title/news)
        
        ordering: <create_time; rating>
            <-rating> will be sort by popularity (from big to small values)
            <create_time> from old to recent
            <-create_time> from recent to old   # set by default

        search: search is carried out according to body field

"""

"""
    POST    comment/
    This fields are required:
        body
        content_type - name of the model we send comment. ('Title' / 'News')
        object_id - id of the instance. (Title's id/ News's id) {'object_id': 13}

    parent_comment - id on a parrent comment


    PATCH   comment/pk/
        body


content_object is a dict. it's include obj name and its slug. 
"content_object": {
        "obj": "Title",
        "slug": "vinland-saga"
    }
"""

"""
if we send delete method to comment which has replies it will not delete an instance it will just set null to body, author and set is_deleted to True 
delete comment only if there is no childs of it
"""


"""
    PATCH   ...react-comment/2/     where 2 is id of the comment
    
    status. -1 for delete
            0 for dislike
            1 for like

"""