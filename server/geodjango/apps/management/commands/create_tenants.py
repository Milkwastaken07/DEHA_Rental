from typing import List
from apps.models import Tenant, Property  
class Command(BaseCommand):
    help = 'Seed database with initial Tenants data'
    def insertTenantData(self, tenants: List[dict]) -> str:
        for tenant in tenants:
            try:
                # Tạo hoặc cập nhật Tenant
                obj, created = Tenant.objects.update_or_create(
                    id=tenant['id'],
                    defaults={
                        'cognitoId': tenant['cognitoId'],
                        'name': tenant['name'],
                        'email': tenant['email'],
                        'phoneNumber': tenant['phoneNumber'],
                    }
                )

                # Gán các quan hệ many-to-many
                if 'properties' in tenant:
                    property_objs = Property.objects.filter(id__in=tenant['properties'])
                    obj.properties.set(property_objs)

                if 'favorites' in tenant:
                    favorite_objs = Property.objects.filter(id__in=tenant['favorites'])
                    obj.favorites.set(favorite_objs)

                obj.save()

            except Exception as e:
                raise Exception(f"Lỗi khi thêm tenant ID {tenant['id']}: {str(e)}")

        return "Insert Tenant data successfully"
