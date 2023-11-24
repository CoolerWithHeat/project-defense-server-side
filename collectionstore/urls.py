from collection.views import *
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('CreateCl/', CreateCollection.as_view()),
    path('GetCL/', GetIndividualCollections.as_view()),
    path('CreateIT/<int:CL_id>/', CreateItem.as_view()),
    path('getItem/<int:item_id>/', GetItem.as_view()),
    path('Get-All-Items/<int:CL_id>/', get_Collection_items.as_view()),
    path('SignUp/', Authentication.as_view()),
    path('Login/', Login.as_view()),
    path('users-collections/', get_Collections.as_view()),
    path('edit_item/<int:item_id>/', edit_item.as_view()),
    path('delete_item/<int:item_id>/', delete_item.as_view()),
    path('delete_collections/', delete_collection.as_view()),
    path('getCustomFields/<int:CL_id>/', RetrieveCustomFields.as_view()),
    path('SaveCustom_Field/<int:CL_ID>/', SaveCustom_Field.as_view()),
    path('Search/', SearchDB.as_view()),
    path('LeaveComment/<int:IT_ID>/', Save_Comment.as_view()),
    path('MainDisplayData/', MainDisplay.as_view()),
    path('GetUsers/', GetUsers.as_view()),
    path('blockUser/', BlockUser.as_view()),
    path('UnblockUser/', UnBlockUser.as_view()),
    path('DeleteUser/', DeleteUser.as_view()),
    path('CheckAdmin/', CheckAdmin.as_view()),
    path('GrantAdmin/', GrantAdmin.as_view()),
    path('RemoveAdmin/', RemoveAdmin.as_view()),
    # path('advancedSearch/', TrialSearch.as_view()),
]