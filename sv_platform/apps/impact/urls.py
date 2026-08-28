    path('ai/chat/', api_views.ai_chat, name='ai_chat'),
    path('ai/chat/', api_views.ai_chat, name='ai_chat'),

# Conversation URLs
path('conversations/save/', api_views.save_conversation, name='save-conversation'),
path('conversations/list/', api_views.get_conversations, name='list-conversations'),
path('conversations/<int:conversation_id>/', api_views.get_conversation, name='get-conversation'),

path('api/vcse/save/', impact_api.save_vcse_result, name='save_vcse_result'),
path('api/vcse/list/', impact_api.list_vcse_results, name='list_vcse_results'),

from django.urls import path
from . import api_views, export_views

urlpatterns = [
    # ... existing URLs ...
    
    # Export endpoints
    path('export/excel/', export_views.ExcelExportView.as_view(), name='export_excel'),
    path('export/pdf/', export_views.PDFExportView.as_view(), name='export_pdf'),
    path('export/csv/', export_views.CSVExportView.as_view(), name='export_csv'),
]