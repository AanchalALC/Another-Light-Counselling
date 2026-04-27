from django.urls import path, re_path
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView  # <-- Import this

from .sitemaps import PostSiteMap, PostTypeSiteMap, StaticSiteMap
from . import views

sitemaps = {
    'static': StaticSiteMap,
    'posts': PostSiteMap,
    'types': PostTypeSiteMap
}

urlpatterns = [
    path('', views.index, name='index'),
    
    path('about/swathi-priya-dev/', RedirectView.as_view(url='/about/swathi-priya/', permanent=True)),
    path('team/dhruvi-patel', RedirectView.as_view(url='/about/dhruvi-patel/', permanent=True)),
    path('team/naveen-coo', RedirectView.as_view(url='/about/naveen-coo/', permanent=True)),
    path('team/kasim', RedirectView.as_view(url='/about/kasim/', permanent=True)),
    path('team/sujoy-sdm', RedirectView.as_view(url='/about/sujoy-sdm/', permanent=True)),
    path('team/swathi-priya-dev', RedirectView.as_view(url='/about/swathi-priya/', permanent=True)),
    path('team/aanchal-narang', RedirectView.as_view(url='/about/aanchal-narang/', permanent=True)),
    path('team/yashwi-chopra', RedirectView.as_view(url='/about/yashwi-chopra/', permanent=True)),
    path('team/hrishti-bhawnani', RedirectView.as_view(url='/about/hrishti-bhawnani/', permanent=True)),
    path('team/aanchal-narang-theythem', RedirectView.as_view(url='/about/aanchal-narang/', permanent=True)),
    path('team/sejal-bajargan', RedirectView.as_view(url='/about/sejal-bajargan/', permanent=True)),
    path('team/amit-hehim', RedirectView.as_view(url='/about', permanent=True)),
    path('team/naveen-hehim', RedirectView.as_view(url='/about/naveen-coo/', permanent=True)),
    path('team/swathi-priya-sheher', RedirectView.as_view(url='/about/swathi-priya/', permanent=True)),
    path('blog/page/', RedirectView.as_view(url='/blog/', permanent=True)),
    path("about/'deki", RedirectView.as_view(url='/about', permanent=True)),


    path('psychological-counselling-therapy', views.psychologicalCounsellingTherapy, name='psychological-counselling-therapy'),
    path('psychological-counselling-therapy/', views.psychologicalCounsellingTherapy, name='psychological-counselling-therapy'),
    path('psychological-counselling-therapy-thankyou', views.pctThankYou, name='psychological-counselling-therapy-thankyou'),
    path('psychological-counselling-therapy-thankyou/', views.pctThankYou, name='psychological-counselling-therapy-thankyou'),

    path('about', views.about, name='about'),

    path('faqs/', views.faqs, name='faqs'),

    path('resources', views.resources, name='resources'),
    path('resources/', views.resources, name='resources'),

    path('reviews', views.reviews, name='reviews'),
    path('reviews/', views.reviews, name='reviews'),

    path('contact', views.contact, name='contact'),
    path('contact/', RedirectView.as_view(url='/contact', permanent=True)),

    path('policy/<slug:slug>', views.policy, name='policy'),
    path('committee/<slug:slug>', views.committee, name='committee'),

    path('services', views.services, name='services'),
    path('services/', views.services, name='services'),
    path('service/<slug:slug>', views.service, name='service'),

    path('doifeels', views.doifeels, name='doifeels'),
    path('doifeels/', views.doifeels, name='doifeels'),
    path('doifeel/<slug:slug>', views.doifeel, name='doifeel'),

    path('careers', views.careers, name='careers'),
    path('careers/', views.careers, name='careers'),
    path('jd/<slug:slug>', views.jd, name='jd'),

    path('post/<slug:slug>', views.post, name='post'),
    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # You can keep these if you still want /team as a list page
    path('team', views.team_list, name='team'),
    path('team/', views.team_list, name='team'),

    # Profile detail should now live under /about/<slug>
    path('about/<slug:slug>/', views.member_profile, name='member-profile'),

    re_path(r"^aanchal-onboarding-plan/?$", views.onboarding_plan, name="onboarding_plan"),
    
    path('about/<slug:slug>/blogs', views.member_blog_list, name='member-blog-list'),
    path('about/<slug:slug>/blogs/', views.member_blog_list, name='member-blog-list'),

    path('about/<slug:slug>/blogs/<slug:post_slug>', views.member_blog_detail, name='member-blog-detail'),
    path('about/<slug:slug>/blogs/<slug:post_slug>/', views.member_blog_detail, name='member-blog-detail'),
]