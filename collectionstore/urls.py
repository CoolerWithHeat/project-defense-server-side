from collection.views import *
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('CreateCl/', CreateCollection.as_view()),
    path('CreateIT/<int:CL_id>/', CreateItem.as_view()),
    path('getItem/<int:item_id>/', GetItem.as_view()),
    path('Get-All-Items/<int:CL_id>/', get_Collection_items.as_view()),
    path('SignUp/', Authentication.as_view()),
]