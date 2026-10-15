from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
    #Первый класс разрешает редактировать и удалять объект только его автору, оставляя чтение доступным


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and getattr(request.user, "role", None) == "admin")
    #Второй разрешает доступ только пользователю с ролью admin