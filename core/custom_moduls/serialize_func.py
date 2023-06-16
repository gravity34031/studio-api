from core.models import Title, AlternativeTitle
from textdistance import overlap as text_similarity
from .constants import PERCENT_OF_SIMILARITY_FOR_RELATED_TITLES




def create_alternative_title(instance, alternative_title_data):
    alt_titles = alternative_title_data.split(';')
    alt_titles = [str(s.strip()) for s in alt_titles if s]
    bulk = []
    for title in alt_titles:
        bulk.append(AlternativeTitle(title=title, anime=instance))
    AlternativeTitle.objects.bulk_create(bulk)



def get_list_pk_of_similarity(string, sequence):
    # res = []
    # for instance in sequence:
    #     if text_similarity.normalized_similarity(string, str(instance.get('title'))) >= PERCENT_OF_SIMILARITY_FOR_RELATED_TITLES:
    #         res.append(instance.get('pk'))
    # return res
    return [instance.get('pk') for instance in sequence if text_similarity.normalized_similarity(string, str(instance.get('title'))) >= PERCENT_OF_SIMILARITY_FOR_RELATED_TITLES]

def create_related_titles(instance, auto_related, related_lists_data, update=False):
    if auto_related: # if auto_related_list is True: generate related_lists automaticly
        title_list = Title.objects.values('pk', 'title') # list to avoid lazy queryset in loop
        title = instance.title # current string title

        # get title list with similarity title greater then constant (0.8)
        related_title_list = get_list_pk_of_similarity(string=title, sequence=title_list)
        # related_title_list is a list of title's PK

        if instance.pk in related_title_list: # delete pk of current Title 
            related_title_list.remove(instance.pk)

        # for update add to exist related_lists new one
        # for post create related_lists relationship 
        instance.related_lists.add(*related_title_list)

    else: # else - auto_related_list is False
        if related_lists_data: # if related_lists is in request
            related_lists = [i.strip() for i in related_lists_data.split(';') if i]
            related_lists_instances = Title.objects.filter(slug__in=related_lists).values('pk') # get titles related to the instance
            related_title_list = [i.get('pk') for i in related_lists_instances if i.get('pk') is not instance.pk] # convert dict to list

            
            if update: # rewrite exists related_lists
                instance.related_lists.set(related_title_list)
            else: # create related_lists relationship
                instance.related_lists.add(*related_title_list)