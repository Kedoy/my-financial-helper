from django.urls import path
from apps.analytics.views import (
    SummaryView,
    DailyTrendView,
    MonthlyTrendView,
    AIInsightsView,
    ExpenseForecastView,
    ForecastSummaryView,
    CategoryForecastsView,
)

urlpatterns = [
    path('summary/', SummaryView.as_view(), name='analytics-summary'),
    path('daily/', DailyTrendView.as_view(), name='analytics-daily'),
    path('monthly/', MonthlyTrendView.as_view(), name='analytics-monthly'),
    path('ai-insights/', AIInsightsView.as_view(), name='analytics-ai-insights'),
    path('forecast/', ExpenseForecastView.as_view(), name='analytics-forecast'),
    path('forecast/summary/', ForecastSummaryView.as_view(), name='analytics-forecast-summary'),
    path('forecast/categories/', CategoryForecastsView.as_view(), name='analytics-forecast-categories'),
]
