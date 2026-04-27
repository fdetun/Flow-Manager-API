import logging

from fastapi import APIRouter, HTTPException
from starlette import status

from app.models.schemas import FlowRequest, FlowResult
from app.services.flow_service import execute_flow, validate_flow

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/flows/run", response_model=FlowResult)
async def run_flow_endpoint(request: FlowRequest) -> FlowResult:
    logger.info("Running flow '%s' (id=%s)", request.flow.name, request.flow.id)
    try:
        result = await execute_flow(request.flow)
        logger.info("Flow '%s' finished with status=%s", request.flow.id, result.status)
        return result
    except Exception as e:
        logger.exception("Unexpected error running flow '%s'", request.flow.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/flows/validate")
def validate_flow_endpoint(request: FlowRequest) -> dict:
    logger.info("Validating flow '%s' (id=%s)", request.flow.name, request.flow.id)
    try:
        result = validate_flow(request.flow)
        logger.info("Flow '%s' is valid", request.flow.id)
        return result
    except ValueError as e:
        logger.warning("Flow '%s' failed validation: %s", request.flow.id, e.args[0])
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.args[0])
    except Exception as e:
        logger.exception("Unexpected error validating flow '%s'", request.flow.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
