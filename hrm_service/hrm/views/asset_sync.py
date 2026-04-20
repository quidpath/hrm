"""
HRM Asset Sync Views
Handles asset synchronization from Inventory Service
"""
import logging
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from hrm_service.hrm.models.asset import Asset, AssetLocationHistory

logger = logging.getLogger(__name__)


def generate_asset_tag(product_id: str, corporate_id: str) -> str:
    """Generate a unique asset tag"""
    # Use first 8 chars of product_id
    product_short = str(product_id).replace('-', '')[:8].upper()
    # Use first 4 chars of corporate_id
    corp_short = str(corporate_id).replace('-', '')[:4].upper()
    return f"AST-{corp_short}-{product_short}"


@api_view(['POST'])
def sync_asset(request):
    """
    Sync asset from inventory
    
    POST /api/hrm/assets/sync/
    
    Expected payload:
    {
        "product_id": "uuid",
        "operation": "create|update|delete",
        "product_name": "Asset Name",
        "product_type": "storable",
        "description": "Description"
    }
    """
    try:
        data = request.data
        corporate_id = request.corporate_id
        
        # Validate required fields
        if not data.get('product_id'):
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('operation'):
            return Response(
                {'error': 'operation is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        operation = data['operation']
        product_id = data['product_id']
        
        if operation == 'create':
            # Check if already exists
            if Asset.objects.filter(
                product_id=product_id,
                corporate_id=corporate_id
            ).exists():
                return Response(
                    {'message': 'Asset already exists'},
                    status=status.HTTP_200_OK
                )
            
            # Generate asset tag
            asset_tag = generate_asset_tag(product_id, corporate_id)
            
            # Ensure unique asset tag
            counter = 1
            original_tag = asset_tag
            while Asset.objects.filter(asset_tag=asset_tag).exists():
                asset_tag = f"{original_tag}-{counter}"
                counter += 1
            
            # Create asset
            asset = Asset.objects.create(
                product_id=product_id,
                asset_tag=asset_tag,
                name=data.get('product_name', 'Unnamed Asset'),
                description=data.get('description', ''),
                product_type=data.get('product_type', ''),
                status='available',
                corporate_id=corporate_id,
                synced_from_inventory=True
            )
            
            logger.info(f"Created HRM asset {asset.id} from inventory sync")
            
            return Response({
                'id': str(asset.id),
                'asset_tag': asset.asset_tag,
                'product_id': str(asset.product_id),
                'name': asset.name,
                'message': 'Asset created successfully'
            }, status=status.HTTP_201_CREATED)
            
        elif operation == 'update':
            # Get existing asset
            try:
                asset = Asset.objects.get(
                    product_id=product_id,
                    corporate_id=corporate_id
                )
            except Asset.DoesNotExist:
                # Create if doesn't exist
                asset_tag = generate_asset_tag(product_id, corporate_id)
                counter = 1
                original_tag = asset_tag
                while Asset.objects.filter(asset_tag=asset_tag).exists():
                    asset_tag = f"{original_tag}-{counter}"
                    counter += 1
                
                asset = Asset.objects.create(
                    product_id=product_id,
                    asset_tag=asset_tag,
                    name=data.get('product_name', 'Unnamed Asset'),
                    description=data.get('description', ''),
                    product_type=data.get('product_type', ''),
                    status='available',
                    corporate_id=corporate_id,
                    synced_from_inventory=True
                )
                
                logger.info(f"Created HRM asset {asset.id} (update operation)")
                
                return Response({
                    'id': str(asset.id),
                    'asset_tag': asset.asset_tag,
                    'product_id': str(asset.product_id),
                    'name': asset.name,
                    'message': 'Asset created successfully'
                }, status=status.HTTP_201_CREATED)
            
            # Update fields
            if 'product_name' in data:
                asset.name = data['product_name']
            if 'description' in data:
                asset.description = data['description']
            if 'product_type' in data:
                asset.product_type = data['product_type']
            
            asset.save()
            
            logger.info(f"Updated HRM asset {asset.id} from inventory sync")
            
            return Response({
                'id': str(asset.id),
                'asset_tag': asset.asset_tag,
                'product_id': str(asset.product_id),
                'name': asset.name,
                'message': 'Asset updated successfully'
            }, status=status.HTTP_200_OK)
            
        elif operation == 'delete':
            # Soft delete - mark as retired
            try:
                asset = Asset.objects.get(
                    product_id=product_id,
                    corporate_id=corporate_id
                )
                asset.status = 'retired'
                asset.is_active = False
                asset.save(update_fields=['status', 'is_active', 'updated_at'])
                
                logger.info(f"Deleted (retired) HRM asset {asset.id}")
                
                return Response({
                    'message': 'Asset retired successfully'
                }, status=status.HTTP_200_OK)
            except Asset.DoesNotExist:
                return Response({
                    'message': 'Asset not found'
                }, status=status.HTTP_200_OK)
        
        else:
            return Response(
                {'error': f'Invalid operation: {operation}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        logger.error(f"Error syncing asset: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to sync asset: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def update_asset_location(request):
    """
    Update asset location
    
    POST /api/hrm/assets/location/
    
    Expected payload:
    {
        "product_id": "uuid",
        "from_location": "Warehouse A",
        "to_location": "Office B",
        "move_date": "2024-01-15T10:30:00Z",
        "notes": "Moved for project"
    }
    """
    try:
        data = request.data
        corporate_id = request.corporate_id
        user_id = request.user_id
        
        # Validate required fields
        if not data.get('product_id'):
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('to_location'):
            return Response(
                {'error': 'to_location is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get asset
        asset = get_object_or_404(
            Asset,
            product_id=data['product_id'],
            corporate_id=corporate_id
        )
        
        # Parse move date
        move_date = data.get('move_date')
        if move_date:
            move_date = parse_datetime(move_date)
        if not move_date:
            move_date = datetime.now()
        
        # Create location history record
        history = AssetLocationHistory.objects.create(
            asset=asset,
            from_location=data.get('from_location', asset.current_location),
            to_location=data['to_location'],
            moved_at=move_date,
            moved_by=user_id,
            notes=data.get('notes', ''),
            corporate_id=corporate_id
        )
        
        # Update asset current location
        asset.current_location = data['to_location']
        asset.save(update_fields=['current_location', 'updated_at'])
        
        logger.info(
            f"Updated asset {asset.asset_tag} location: "
            f"{history.from_location} → {history.to_location}"
        )
        
        return Response({
            'asset_tag': asset.asset_tag,
            'from_location': history.from_location,
            'to_location': history.to_location,
            'message': 'Asset location updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Asset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating asset location: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to update asset location: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_assets(request):
    """
    List all assets
    
    GET /api/hrm/assets/
    """
    try:
        corporate_id = request.corporate_id
        
        assets = Asset.objects.filter(
            corporate_id=corporate_id,
            is_active=True
        ).order_by('asset_tag')
        
        data = [{
            'id': str(asset.id),
            'asset_tag': asset.asset_tag,
            'product_id': str(asset.product_id),
            'name': asset.name,
            'product_type': asset.product_type,
            'current_location': asset.current_location,
            'status': asset.status,
            'assigned_to': str(asset.assigned_to) if asset.assigned_to else None,
        } for asset in assets]
        
        return Response({
            'count': len(data),
            'assets': data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to list assets: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
