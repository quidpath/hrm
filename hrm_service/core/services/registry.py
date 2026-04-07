# hrm_service/core/services/registry.py
from datetime import datetime
from typing import Any, Dict, Optional, Type, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Q, QuerySet


class ServiceRegistry:
    """
    Dynamic CRUD service registry for HRM service.
    """

    def get_model_class(self, model_name: str) -> Type[Model]:
        """
        Retrieve the model class based on its name.
        """
        content_type = ContentType.objects.filter(model=model_name.lower()).first()
        if not content_type:
            raise ValueError(f"Model '{model_name}' is not recognized.")
        return content_type.model_class()

    def serialize_data(self, data: Any) -> Any:
        """
        Convert model instances or QuerySets into JSON-serializable dicts.
        """
        if isinstance(data, Model):
            return self.serialize_instance(data)
        elif isinstance(data, QuerySet):
            return [self.serialize_instance(instance) for instance in data]
        return data

    def serialize_instance(self, instance: Model) -> dict:
        data = {}
        for field in instance._meta.fields:
            value = getattr(instance, field.name)
            if field.is_relation:
                data[f"{field.name}_id"] = getattr(instance, f"{field.name}_id")
            data[field.name] = value.isoformat() if isinstance(value, datetime) else value
        return data

    def database(
        self,
        model_name: str,
        operation: str,
        instance_id: Optional[Any] = None,
        data: Optional[Union[Dict[str, Any], Q]] = None,
        soft: bool = True,
    ) -> Any:
        """
        Perform CRUD operations dynamically based on the model name and operation.
        """
        model_class = self.get_model_class(model_name)
        data = data or {}

        if operation == "create":
            instance = model_class.objects.create(**data)
            return self.serialize_instance(instance)
            
        elif operation == "get":
            if not data:
                raise ValueError("Filter criteria must be provided for 'get' operation.")
            instance = model_class.objects.get(**data)
            return self.serialize_instance(instance)
            
        elif operation == "update":
            if instance_id is None:
                raise ValueError("Instance ID is required for 'update' operation.")
            instance = model_class.objects.get(pk=instance_id)
            for key, value in data.items():
                setattr(instance, key, value)
            instance.save()
            return self.serialize_instance(instance)
            
        elif operation == "delete":
            if instance_id is None:
                raise ValueError("Instance ID is required for 'delete' operation.")
            instance = model_class.objects.get(pk=instance_id)
            if soft and hasattr(instance, 'is_active'):
                instance.is_active = False
                instance.save()
            else:
                instance.delete()
            return {"deleted": True}
            
        elif operation == "filter":
            query = Q()
            if isinstance(data, Q):
                query &= data
            elif isinstance(data, dict):
                query &= Q(**data)
            else:
                raise ValueError("Data for 'filter' must be a Q object or dict.")
            queryset = model_class.objects.filter(query)
            return self.serialize_data(queryset)
            
        elif operation == "all":
            queryset = model_class.objects.all()
            return self.serialize_data(queryset)
            
        else:
            raise ValueError(f"Unsupported operation: {operation}")
