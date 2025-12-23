"""
URL configuration for PGproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from WeekendApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Login),
    path('login/', views.Login),
    path('signup/', views.signup),
    path('home/',views.home, name="home"),
    path('logout/', views.Logout),
    path('about/',views.about),
    path('pgs/',views.pgs),
    path('feedback/',views.feedback_view),
    # path('thank_you/',views.feedback_thank_you),
    # path('paymentdone/',views.paymentdone),
    # path('pgbooked/',views.pgbooked),
    path('bookmarks/',views.user_bookmarks),
    path('owners/',views.owners),
    path('pg/<int:pg_id>/',views.singlepg, name='singlepg'),
    path('add_to_bookmarks/<int:pg_id>/', views.add_to_bookmarks, name='add_to_bookmarks'),
    path('bookmark/<int:bookmark_id>/remove_pg/',views.remove_from_bookmark, name='remove_pg'),
    path("book/<int:pg_id>/", views.book_pg, name="book_pg"),
    path("booking-success/", lambda r: render(r, "booking_success.html"), name="booking_success"),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path("villas/", views.villa_list, name="villa_list"),
    path("admin-dashboard/", views.custom_admin_dashboard, name="admin_dashboard"),
    path("api/recommend/", views.recommend_place, name="recommend_place"),
    path('booking/<int:booking_id>/receipt/', views.generate_receipt, name='generate_receipt'),

                  # Owner CRUD

                  path("admin-panel/manage-data/", views.manage_data, name="manage_data"),

                  # Owner CRUD
                  path("admin-panel/owners/", views.owner_list, name="owner_list"),
                  path("admin-panel/owners/add/", views.owner_create, name="owner_create"),
                  path("admin-panel/owners/edit/<int:id>/", views.owner_update, name="owner_update"),
                  path("admin-panel/owners/delete/<int:id>/", views.owner_delete, name="owner_delete"),

                  # PG CRUD
                  path("admin-panel/pgs/", views.pg_list, name="pg_list"),
                  path("admin-panel/pgs/add/", views.pg_create, name="pg_create"),
                  path("admin-panel/pgs/edit/<int:id>/", views.pg_update, name="pg_update"),
                  path("admin-panel/pgs/delete/<int:id>/", views.pg_delete, name="pg_delete"),


] + static(settings.STATIC_URL)