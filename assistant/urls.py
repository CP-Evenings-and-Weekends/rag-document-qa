from django.urls import path

from . import views

# You will add your endpoints here during the lesson.
urlpatterns = [
   path("documents/", views.document_list, name="document-list"),  
   path("ask/", views.ask_question, name="ask-question"),
]
