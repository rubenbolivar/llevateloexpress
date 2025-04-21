from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.FinancingPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('simulations/', views.SimulationListView.as_view()),
    path('simulate/', views.SimulateFinancingView.as_view()),
    path('save-simulation/', views.SaveSimulationView.as_view()),
] 