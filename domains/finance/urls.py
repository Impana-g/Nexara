# domains/finance/urls.py

from rest_framework.routers import DefaultRouter
from .views import PortfolioViewSet, HoldingViewSet, PortfolioReviewViewSet

router = DefaultRouter()
router.register(r'portfolios',        PortfolioViewSet,       basename='portfolio')
router.register(r'holdings',          HoldingViewSet,         basename='holding')
router.register(r'portfolio-reviews', PortfolioReviewViewSet, basename='portfolio-review')

urlpatterns = router.urls