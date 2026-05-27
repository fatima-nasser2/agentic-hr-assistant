from fastapi import APIRouter, Depends
from api.models import SourcesResponse, SourceInfo
from api.dependencies import get_current_employee

router = APIRouter(prefix="/sources", tags=["Sources"])

@router.get("", response_model=SourcesResponse)
async def get_sources(current_employee: dict = Depends(get_current_employee)):
    """Returns all available knowledge sources."""
    return SourcesResponse(
        sources=[
            SourceInfo(
                id="faiss",
                name="HR Policy Documents",
                description="Company HR policies including leave, remote work, hiring, compensation, and code of conduct",
                document_count=5
            ),
            SourceInfo(
                id="sql",
                name="Employee Database",
                description="Personal employee records including leave balances, salary, and review dates",
                document_count=51
            ),
            SourceInfo(
                id="internal_kb",
                name="Internal Knowledge Base",
                description="Company announcements, team structure, onboarding guides, and IT guidelines",
                document_count=4
            )
        ]
    )