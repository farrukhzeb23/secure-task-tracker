from typing import List

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory that creates a dependency to check if user has required roles.

    Usage:
    @router.get("/admin-only")
    async def admin_endpoint(user: User = Depends(require_roles(["admin"]))):
        return {"message": "Admin access granted"}
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No roles assigned to user",
            )

        user_role_names = [role.name for role in current_user.roles]

        # Check if user has any of the required roles
        if not any(role in user_role_names for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}",
            )

        return current_user

    return role_checker


def require_admin():
    """Shortcut for admin-only access."""
    return require_roles(["admin"])
