from django.urls import path
from django.shortcuts import redirect
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', lambda request: redirect('/login/')), 
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registrar_usuario),
    path('inicio/', views.inicio, name='inicio'),  
    path('logout/', views.cerrar_sesion),
    path('productos/', views.productos),  
    path('libros/agregar/', views.agregar_libro),
    path('libros/editar/<int:libro_id>/', views.editar_libro),
    path('libros/eliminar/<int:libro_id>/', views.eliminar_libro),
    path('comprar/<int:libro_id>/', views.comprar_libro),
    path('solicitudes/', views.gestionar_solicitudes),
    path('completar/<int:orden_id>/', views.completar_orden),
    path('mis_solicitudes/', views.mis_solicitudes),
    path('ventas/', views.reporte_ventas),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
