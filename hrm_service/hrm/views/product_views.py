"""
Product/Asset Views for HRM
Queries inventory service for product information
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from hrm_service.services.inventory_client import InventoryClient

logger = logging.getLogger(__name__)


@api_view(['GET'])
def search_assets(request):
    """
    Search assets/products from inventory
    
    GET /api/hrm/assets/search/?q=query
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=400)
        
        inventory = InventoryClient()
        products = inventory.search_products(query, request.corporate_id)
        
        return Response({
            'count': len(products),
            'assets': products
        })
        
    except Exception as e:
        logger.error(f"Error searching assets: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_asset(request, product_id):
    """
    Get single asset/product from inventory
    
    GET /api/hrm/assets/{product_id}/
    """
    try:
        inventory = InventoryClient()
        product = inventory.get_product(product_id, request.corporate_id)
        
        if not product:
            return Response({'error': 'Asset not found'}, status=404)
        
        return Response(product)
        
    except Exception as e:
        logger.error(f"Error getting asset: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def list_assets(request):
    """
    List all assets/products
    
    GET /api/hrm/assets/
    """
    try:
        inventory = InventoryClient()
        products = inventory.list_products_for_sale(request.corporate_id)
        
        return Response({
            'count': len(products),
            'assets': products
        })
        
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def get_assets_bulk(request):
    """
    Get multiple assets at once
    
    POST /api/hrm/assets/bulk/
    Body: {"product_ids": ["uuid1", "uuid2"]}
    """
    try:
        product_ids = request.data.get('product_ids', [])
        if not product_ids:
            return Response({'error': 'product_ids is required'}, status=400)
        
        inventory = InventoryClient()
        products = inventory.get_products_bulk(product_ids, request.corporate_id)
        
        return Response({
            'count': len(products),
            'assets': products
        })
        
    except Exception as e:
        logger.error(f"Error getting assets bulk: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def check_asset_stock(request, product_id):
    """
    Check stock level for an asset
    
    GET /api/hrm/assets/{product_id}/stock/
    """
    try:
        inventory = InventoryClient()
        stock = inventory.get_stock_level(product_id, request.corporate_id)
        
        if not stock:
            return Response({'error': 'Stock information not available'}, status=404)
        
        return Response(stock)
        
    except Exception as e:
        logger.error(f"Error checking stock: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)
