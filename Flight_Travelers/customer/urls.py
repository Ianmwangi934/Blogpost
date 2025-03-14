from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login_view",views.login_view, name="login_view"),
    path("signup", views.signup, name="signup"),
    path("profile_view/<str:username>/", views.profile_view, name="profile_view"),
    path("airlines", views.airlines, name="airlines"),
    path("airlines/<int:airline_id>/",views.airline_detail, name="airline_detail"),
    path("airlines/<str:iata_code>/flights/",views.flight_data_view,name="flight_data_view"),
    path("book_flight", views.book_flight_view, name="book_flight_view"),
    path("airlines/<str:iata_code>/search", views.airlines_search_view,name="airline_search_view"),
    path("support/submit/", views.submit_ticket, name="submit_ticket"),
    path("support/ticket",views.ticket_list, name="ticket_list"),
    path("support/dashboard/",views.support_dashboard, name="support_dashboard"),
    path("support/ticket/<int:ticket_id>/",views.ticket_detail, name="ticket_detail")

]