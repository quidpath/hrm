"""
Asset URLs for HRM
Query endpoints for inventory service
"""
from django.urls import path
from hrm_service.hrm.views.product_views import (
    search_assets,
    get_asset,
    list_assets,
    get_assets_bulk,
    check_asset_stock,
)

urlpatterns = [
    path("", list_assets, name="list_assets"),
    path("search/", search_assets, name="search_assets"),
    path("bulk/", get_assets_bulk, name="get_assets_bulk"),
    path("<uuid:product_id>/", get_asset, name="get_asset"),
    path("<uuid:product_id>/stock/", check_asset_stock, name="check_asset_stock"),
]
