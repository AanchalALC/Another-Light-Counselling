import os
import re
from urllib.parse import urlparse, parse_qs

from django.contrib.sites.models import Site
# from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse

from .models import Post, PostType, FAQ, Resource, Review, Member, Statistic, ContactDetails, Service,DoIFeel, Policy, Committee, DynamicContent , Jd, OnboardingPlan
from .forms import ContactForm, PpcContactForm


# ------------------- HELPERS --------------------------

def get_paragraph_preview(content):
    preview = ''

    try:
        first_para = str(content).split('</p>')[0].split('<p>')[1]
        first_twenty = first_para.split(' ')[:35]
        # remove comma from last
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]

        preview = '{}...'.format(' '.join(first_twenty), '...')
    except IndexError as ie:
        print(str(ie))
        preview = content

    return preview

def get_protocol():
    if os.environ.get('DEBUG').lower() == 'true':
        return 'http'
    else:
        return 'https'

def get_full_url(ending):
    return '%s://%s%s' % (get_protocol(), Site.objects.get_current().domain, ending)

def get_header_contacts():
    contactdetails = ContactDetails.objects.all()
    h_contacts = {}

    for cd in contactdetails:
        h_contacts[cd.key] = cd

    return h_contacts


# meet our team youtube intro
# def get_youtube_embed_url(orig_url):
#     """Return a valid YouTube embed URL with autoplay & mute, or None."""
#     if not orig_url:
#         return None

#     parsed = urlparse(orig_url)
#     video_id = None

#     # case 1: youtu.be/VIDEO_ID
#     if 'youtu.be' in parsed.netloc:
#         video_id = parsed.path.lstrip('/')

#     # case 2: youtube.com/watch?v=VIDEO_ID
#     elif 'youtube.com' in parsed.netloc:
#         qs = parse_qs(parsed.query)
#         video_id = qs.get('v', [None])[0]

#     if not video_id:
#         return None

#     # autoplay=1&mute=1 so browsers will actually play it
#     return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"


# ------------------- VIEWS --------------------------

def pctThankYou(request):
    return render(request, 'pct_thankyou.html')

def psychologicalCounsellingTherapy(request):

    if request.method == 'POST':
        
        cform = PpcContactForm(request.POST)        
        if cform.is_valid():
            cform.save()

        return redirect('psychological-counselling-therapy-thankyou')

    else:
        form = PpcContactForm()
        whatsappnum = ContactDetails.objects.get(key='phone')
        context = {
            'form': form,
            'whatsappnum': whatsappnum,
        }
        return render(request, 'psychological_counselling_therapy.html', context=context)


def index(request):

    # GET STATS
    stats = Statistic.objects.all()

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')

    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 
    
    # GET DYANMIC CONTENT
    s1 = DynamicContent.objects.get(key='home_section_1')
    s2 = DynamicContent.objects.get(key='home_section_2')
    s3 = DynamicContent.objects.get(key='home_section_3')

    # set context
    context = {
        'stats': stats,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels': doifeels,
        #'howtofeels':howtofeels,
        'h_contacts': get_header_contacts(),
        's1': s1,
        's2': s2,
        's3': s3
    }

    return render(request, 'index.html', context=context)

def about(request):
    # members = Member.objects.all().order_by('order') // order by order id
    members = Member.objects.all().order_by('name')

    # GET CARD CONTENT
    cardcontent = DynamicContent.objects.get(key='about_card')

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    # PROCESSING
    for i in range(0, len(members)):
        memberobj = members[i]
        
        # SET LAYOUT POSITION
        if i == 0 or i%2 == 0:
            memberobj.layout_position = 'right'
        else:
            memberobj.layout_position = 'left'

        # SET TOOLTIP HTMLS
        memberobj.generate_tooltip_markup()

    # CONTEXT
    context = {
        'members': members,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'cardcontent': cardcontent,
        'h_contacts': get_header_contacts()
    }

    return render(request, 'about.html', context=context)

def faqs(request):
    faqs = FAQ.objects.all().order_by('id')

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id') 
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    # GENERATE ALL TOOLTIP HTMLS
    for obj in faqs:
        obj.generate_tooltip_markup()
        print(obj.tippy_answer)

    # SPLIT INTO COLUMNS
    faq1 = faqs[:int(len(faqs)/2)]
    faq2 = faqs[int(len(faqs)/2) :]

    # print(faq1)
    # print(faq2)

    context = {
        'faqs': faqs,
        'faq1': faq1,
        'faq2': faq2,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }
    return render(request, 'faqs.html', context=context)

def resources(request):
    resources = Resource.objects.all().order_by('-id')

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id') 
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    context = {
        'resources': resources,
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'contactdetails': contactdetails,
        'services': services,
        'h_contacts': get_header_contacts()
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
    
    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    reviews_and_doodles = get_review_doodle_list(reviews)
    context = {
        'reviews': reviews_and_doodles,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels' :doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }

    return render(request, 'reviews.html', context=context)

def services(request):
    services = Service.objects.all().order_by('id')
    # reviews_and_doodles = get_review_doodle_list(reviews)

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id') 
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    context = {
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'services': services,
        'contactdetails': contactdetails,
        'h_contacts': get_header_contacts()
    }

    return render(request, 'services.html', context=context)

def service(request, slug):
    # FETCH OBJ
    service_obj=Service.objects.get(slug = str(slug))

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id') 

    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 
 
    # CREATE CONTEXT
    context = {
        'service': service_obj,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels' :doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }
 
    # RETURN
    return render(request, 'service.html', context=context)

def doifeels(request):
    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id') 
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id')    

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')
    
    # reviews_and_doodles = get_review_doodle_list(reviews)

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    context = {
        'doifeels': doifeels,
        # 'howtofeels':howtofeels,
        'services': services,
        'contactdetails': contactdetails,
        'h_contacts': get_header_contacts()
    }

    return render(request, 'doifeels.html', context=context)

def doifeel(request, slug):
    # FETCH OBJ
    doifeel_obj=DoIFeel.objects.get(slug = str(slug))

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    # CREATE CONTEXT
    context = {
        'doifeel': doifeel_obj,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }

    # RETURN
    return render(request, 'doifeel.html', context=context)

def careers(request):
    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET careers
    careers = Jd.objects.all().order_by('id')    

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')
    
    # reviews_and_doodles = get_review_doodle_list(reviews)

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    context = {
        'doifeels': doifeels,
        'careers': careers,
        'services': services,
        'contactdetails': contactdetails,
        'h_contacts': get_header_contacts()
    }

    return render(request, 'careers.html', context=context)

def jd(request, slug):
    
    # FETCH OBJ
    jd_obj= Jd.objects.get(slug = str(slug))

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET DO I FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id')

    # CREATE CONTEXT
    context = {
        'jd': jd_obj,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels':doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }

    # RETURN
    return render(request, 'jd.html', context=context)

def contact(request):

    if request.method == 'POST':
        
        cform = ContactForm(request.POST)        
        if cform.is_valid():
            cform.save()

        return HttpResponseRedirect(reverse('contact') + '#promptoverlay')

    else:
        contactdetails = ContactDetails.objects.all()
        form = ContactForm()

        # GET SERVICES FOR FOOTER
        services = Service.objects.all().order_by('id')

        # GET DO I FEEL
        doifeels = DoIFeel.objects.all().order_by('id')
        
        # GET HOW TO FEEL
        # howtofeels = HowToFeel.objects.all().order_by('id') 

        context = {
            'form': form,
            'contactdetails': contactdetails,
            'services': services,
            'doifeels':doifeels,
            # 'howtofeels':howtofeels,
            'h_contacts': get_header_contacts()
        }


        return render(request, 'contact.html', context=context)

def post(request, slug):
    # FETCH OBJ
    post_obj=Post.objects.get(slug = str(slug))
 
    # HUMAN FRIENDLY DATE
    hfr_date = post_obj.created.strftime('%e %b %Y')
    post_obj.hfr_date = hfr_date

    # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')

    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')

    # INTELLIGENT META TITLE
    metatitle = post_obj.meta_title
    if str(metatitle) == '':
        metatitle = post_obj.title

    # INTELLIGENT META DESCRIPTION
    metadescription = post_obj.meta_description
    if str(metadescription) == '':
        metadescription = get_paragraph_preview(str(post_obj.content))
 
    # CREATE CONTEXT
    context = {
        'title': post_obj.title,
        'metatitle': metatitle,
        'description': metadescription,
        'canon_url': get_full_url(reverse('post', args=[slug])),
        'full_header_url': get_full_url(post_obj.image_file.url),
        'post': post_obj,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels':doifeels,
        'h_contacts': get_header_contacts()
    }
 
    # RETURN
    return render(request, 'post.html', context=context)
 
def blog(request, pageno=1):
    # FETCH ALL POSTS
    # posts = Post.objects.filter(p_type__type_name = typename).exclude(slug='about').order_by('-created', 'title')
    posts = Post.objects.all().order_by('-created', 'title')
    # postscount = len(posts)
 
    # # PAGINATE
    # paginator = Paginator(posts, 10)
    # page_num = int(pageno)
    # page_obj = paginator.get_page(page_num)
    # posts = page_obj.object_list

    # # GET CONTACTS FOR FOOTER
    contactdetails = ContactDetails.objects.all()

    # # GET SERVICES FOR FOOTER
    services = Service.objects.all().order_by('id')
    
    # GET DO I FEEL
    doifeels = DoIFeel.objects.all().order_by('id')
    
    # GET HOW TO FEEL
    # howtofeels = HowToFeel.objects.all().order_by('id') 

    # # HUMAN FRIENDLY DATE
    # for post in posts:
    #     hfr_date = post.created.strftime('%e %b %Y')
    #     post.hfr_date = hfr_date
 
    #     post.preview = str(post.content).split('</p>')[0].split('<p>')[1]
 
    # # SET CONTEXT
    context = {
        'posts': posts,
        # 'postscount': postscount,
        # 'pageinator': paginator,
        # 'page_obj': page_obj,
        'contactdetails': contactdetails,
        'services': services,
        'doifeels' :doifeels,
        # 'howtofeels':howtofeels,
        'h_contacts': get_header_contacts()
    }

    # RETURN
    return render(request, 'posts.html', context=context)
    # return render(request, 'posts.html')

def policy(request, slug):

    # FETCH OBJ
    policy_obj=Policy.objects.get(slug = str(slug))

    context = {
        'policy': policy_obj
    }

    return render(request, 'policy.html', context=context)

def committee(request, slug):

    # FETCH OBJ
    committee_obj=Committee.objects.get(slug = str(slug))

    context = {
        'committee': committee_obj
    }

    return render(request, 'committee.html', context=context)

# meet our team
# def member_profile(request, slug):
#     member = get_object_or_404(Member, slug=slug)
#     embed_url = get_youtube_embed_url(member.intro_video_url)
#     context = {
#         'member': member,
#         'embed_url': embed_url,
#         'contactdetails': ContactDetails.objects.all(),
#         'services': Service.objects.all().order_by('id'),
#         'doifeels': DoIFeel.objects.all().order_by('id'),
#         'h_contacts': get_header_contacts(),
#     }
#     return render(request, 'member_profile.html', context)

def onboarding_plan(request):
    plan = OnboardingPlan.objects.first()
    if not plan:
        return render(request, "onboarding_plan.html", {"plan": None})

    # Prepare steps list for template
    steps = [
        {
            "order": 1,
            "icon": plan.step1_icon.url if plan.step1_icon else "",
            "title": plan.step1_title,
            "detail": plan.step1_detail,
        },
        {
            "order": 2,
            "icon": plan.step2_icon.url if plan.step2_icon else "",
            "title": plan.step2_title,
            "detail": plan.step2_detail,
        },
        {
            "order": 3,
            "icon": plan.step3_icon.url if plan.step3_icon else "",
            "title": plan.step3_title,
            "detail": plan.step3_detail,
        },
    ]

    # Prepare plans list for template
    plans = [
        {
            "name": plan.plan1_name,
            "price": plan.plan1_price,
            "features": [f for f in plan.plan1_features.splitlines() if f.strip()],
            "prerequisites": plan.plan1_prerequisites,
            "is_combo": plan.plan1_is_combo,
        },
        {
            "name": plan.plan2_name,
            "price": plan.plan2_price,
            "features": [f for f in plan.plan2_features.splitlines() if f.strip()],
            "prerequisites": plan.plan2_prerequisites,
            "is_combo": plan.plan2_is_combo,
        },
        {
            "name": plan.plan3_name,
            "price": plan.plan3_price,
            "features": [f for f in plan.plan3_features.splitlines() if f.strip()],
            "prerequisites": plan.plan3_prerequisites,
            "is_combo": plan.plan3_is_combo,
        },
        {
            "name": plan.plan4_name,
            "price": plan.plan4_price,
            "features": [f for f in plan.plan4_features.splitlines() if f.strip()],
            "prerequisites": plan.plan4_prerequisites,
            "is_combo": plan.plan4_is_combo,
        },
        {
            "name": plan.plan5_name,
            "price": plan.plan5_price,
            "features": [f for f in plan.plan5_features.splitlines() if f.strip()],
            "prerequisites": plan.plan5_prerequisites,
            "is_combo": plan.plan5_is_combo,
        },
        {
            "name": plan.plan6_name,
            "price": plan.plan6_price,
            "features": [f for f in plan.plan6_features.splitlines() if f.strip()],
            "prerequisites": plan.plan6_prerequisites,
            "is_combo": plan.plan6_is_combo,
        },
        {
            "name": plan.plan7_name,
            "price": plan.plan7_price,
            "features": [f for f in plan.plan7_features.splitlines() if f.strip()],
            "prerequisites": plan.plan7_prerequisites,
            "is_combo": plan.plan7_is_combo,
        },
        {
            "name": plan.plan8_name,
            "price": plan.plan8_price,
            "features": [f for f in plan.plan8_features.splitlines() if f.strip()],
            "prerequisites": plan.plan8_prerequisites,
            "is_combo": plan.plan8_is_combo,
        },
    ]

    # Prepare renewals list for template
    renewals = [
        {
            "name": plan.renewal1_name,
            "price": plan.renewal1_price,
            "description": plan.renewal1_description,
        },
        {
            "name": plan.renewal2_name,
            "price": plan.renewal2_price,
            "description": plan.renewal2_description,
        },
    ]
    services  = Service.objects.all().order_by('id')
    doifeels  = DoIFeel.objects.all().order_by('id')

    context = {
        "plan": plan,
        "steps": steps,
        "plans": plans,
        "renewals": renewals,
        "h_contacts": get_header_contacts(),
          "services": services, 
        "doifeels": doifeels,
    }
    return render(request, "onboarding_plan.html", context)

