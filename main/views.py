import os

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse

from .models import Post, PostType, FAQ, Resource, Review


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def faqs(request):
    faqs = FAQ.objects.all().order_by('id')

    faq1 = faqs[:int(len(faqs)/2)]
    faq2 = faqs[int(len(faqs)/2) :]

    print(faq1)
    print(faq2)

    context = {
        'faqs': faqs,
        'faq1': faq1,
        'faq2': faq2
    }
    return render(request, 'faqs.html', context=context)

def resources(request):
    resources = Resource.objects.all().order_by('-id')

    context = {
        'resources': resources
    }

    return render(request, 'resources.html', context=context)



def get_review_doodle_list(reviews):
    # CREATE NEEDED OBJECTS
    left_item = {
        'type': 'doodle',
        'position': 'left',
        'art': 'img/reviews/left_arrow1.png'
    }

    right_item_1 = {
        'type': 'doodle',
        'position': 'right',
        'art': 'img/reviews/right_arrow.png'
    }

    right_item_2 = {
        'type': 'doodle',
        'position': 'right',
        'art': 'img/reviews/left_arrow2.png'
    }

    review_item = {
        'type': 'review',
        'position': 'any',
        'obj': None
    }






    # INITIALISE LIST AND OTHER VARS
    review_list = []    

    # VARIABLES NEEDED
    review_indices = []
    num_of_cells = len(reviews) * 2
    
    # DECIDE REVIEW INDICES
    for i in range(0, num_of_cells):
        curr = i
        nex = i+1
        prev = i-1

        if curr == 0:
            continue

        if ( nex % 2 == 0 ) and ( nex % 4 != 0 ):
            review_indices.append(curr)
            continue

        if ( curr % 2 == 0 ) and ( curr % 4 != 0 ):
            review_indices.append(curr)
            continue


    # NOW FILL IN THE POSITIONS
    review_head = 0

    for i in range(0, num_of_cells):

        # FIRST CELL OR IF THE CELL IS A MULTIPLE OF 4, IT'S A LEFT DOODLE
        # AND IS NOT SECOND LAST
        if ( i == 0 ) or ( i % 4 == 0 ):
            # SECOND LAST MUST BE EMPTY
            if ( i + 1 < num_of_cells-1 ):
                review_list.append({
                    'type': 'doodle',
                    'position': 'left',
                    'art': 'img/reviews/left_arrow1.png'
                })
            else:
                review_list.append({
                    'type': 'doodle',
                    'position': 'left',
                    'art': ''
                })

        # IF THE PLACE IS FOR A REVIEW, ADD A REVIEW
        if i in review_indices:            
            review_list.append({
                'type': 'review',
                'position': 'left' if i%2==0 else 'right',
                'obj': reviews[review_head]
            })
            review_head += 1
            continue

        # IF THE CELL IS ODD AND THE NEXT CELL IS A MULTIPLE OF 4, IT'S A RIGHT DOODLE
        # ONLY IF THIS ISN'T THE LAST ELEMENT
        if ( i % 2 != 0 ) and ( (i+1) % 4 == 0 ) and ( i < num_of_cells - 1 ):
            review_list.append(right_item_1)
            continue

    return review_list
    



def reviews(request):
    reviews = Review.objects.all().order_by('-id')
    reviews_and_doodles = get_review_doodle_list(reviews)
    context = {
        'reviews': reviews_and_doodles
    }

    return render(request, 'reviews.html', context=context)


 
def post(request, slug):
    # FETCH OBJ
    post_obj=Post.objects.get(slug = str(slug))
 
    # HUMAN FRIENDLY DATE
    hfr_date = post_obj.created.strftime('%e %b %Y')
    post_obj.hfr_date = hfr_date
 
    # CREATE CONTEXT
    context = {
        'post': post_obj,
    }
 
    # RETURN
    return render(request, 'post.html', context=context)
 
def posts(request, pageno=1):
    # FETCH ALL POSTS
    # posts = Post.objects.filter(p_type__type_name = typename).exclude(slug='about').order_by('-created', 'title')
    posts = Post.objects.all().order_by('-created', 'title')
 
    # PAGINATE
    paginator = Paginator(posts, 10)
    page_num = int(pageno)
    page_obj = paginator.get_page(page_num)
    posts = page_obj.object_list
 
    # HUMAN FRIENDLY DATE
    for post in posts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]
 
    # SET CONTEXT
    context = {
        'posts': posts,
        'pageinator': paginator,
        'page_obj': page_obj,
    }
 
    # RETURN
    return render(request, 'posts.html', context=context)
