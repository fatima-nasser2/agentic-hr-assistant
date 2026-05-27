from fastapi import APIRouter, HTTPException, status
from api.models import LoginRequest, TokenResponse
from api.dependencies import create_access_token
from src.database.query_engine import get_employee_info

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with employee ID to get a JWT access token.
    In production this would verify password/SSO.
    """
    employee = get_employee_info(request.employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee ID '{request.employee_id}' not found"
        )

    token = create_access_token(
        employee_id=employee["employee_id"],
        name=employee["name"]
    )

    return TokenResponse(
        access_token=token,
        employee_id=employee["employee_id"],
        name=employee["name"]
    )