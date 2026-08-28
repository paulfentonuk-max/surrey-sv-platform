
# Export endpoints
from . import export_views
urlpatterns += [
    path('export/excel/', export_views.ExcelExportView.as_view(), name='export_excel'),
    path('export/pdf/', export_views.PDFExportView.as_view(), name='export_pdf'),
]
