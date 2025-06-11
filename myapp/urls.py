from django.contrib import admin
from django.urls import path,include
from myapp import views
urlpatterns = [
    #path('admin/', admin.site.urls),
    path('',views.custom_login,name='login'),
    path('forgotpass/',views.forgotpass,name='forgotpass'),
    path('changepass/',views.changepass,name='changepass'),
    path('profile/',views.profile,name='profile'),
    path('logout/',views.logoutprofile,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('adduser/',views.adduser,name='adduser'),
    path('edituser/<int:user_id>/', views.edituser, name='edituser'),
   
    path('editprofile/<int:id>/',views.editprofile,name='editprofile'),
    
    path('upload/', views.upload, name='upload'),
    path('delete_uploaded_csv/<int:csv_id>/', views.delete_uploaded_csv, name='delete_uploaded_csv'),
    path('export_new_client_policies/', views.export_new_client_policies_excel, name='export_new_client_policies'),
    
    path('policy_report/', views.policy_report_view, name='policy_report'),
    path('policy_report/export/', views.export_policy_excel, name='export_policy_excel'),
    path('company_report/', views.company_wise_report, name='company_report'),
    path('branch_wise/', views.branch_wise_report, name='branch_wise'),
    path('upload/view/<int:csv_id>/', views.view_uploaded_csv, name='view_uploaded_csv'),
    path('new_client_report/', views.new_client_policy_report, name='new_client_report'),
    path('policy_history_report/', views.policy_history_client_wise, name='policy_history_report'),
    path('product_lob_wise/', views.lob_wise_date_breakup_report, name='product_lob_wise'),
    path('agent_wise_commission_report/', views.agent_commission_report, name='agent_wise_commission_report'),
    
    
    
]