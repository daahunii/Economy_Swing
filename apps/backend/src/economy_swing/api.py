import logging
from uuid import uuid4
from typing import Literal
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .application import build_dashboard, relationship, TERMS
from .schemas import ApiError, Dashboard, Horizon, Indicator, Relationship, Sector, Term

logger=logging.getLogger(__name__)
app=FastAPI(title="Economy Swing API",version="0.1.0",description="Read-only synthetic research demo. No live data or investment recommendations.")

@app.middleware("http")
async def request_id(request: Request, call_next):
    request.state.request_id=uuid4().hex
    response=await call_next(request)
    response.headers["X-Request-ID"]=request.state.request_id
    response.headers["Cache-Control"]="no-store"
    return response

@app.exception_handler(RequestValidationError)
async def invalid(request: Request, exc):
    return JSONResponse(status_code=422,content=ApiError(code="INVALID_INPUT",message="지원하는 조회 조건을 확인해 주세요.",request_id=request.state.request_id).model_dump())

def not_found(request):
    return JSONResponse(status_code=404,content=ApiError(code="NOT_FOUND",message="요청한 항목을 찾을 수 없습니다.",request_id=request.state.request_id).model_dump())

@app.get("/health/live")
def live():
    return {"status":"ok","data_mode":"demo"}

@app.get("/health/ready")
def ready():
    build_dashboard()
    return {"status":"ready","data_mode":"demo","database":"not-configured"}

@app.get("/api/v1/dashboard",response_model=Dashboard)
def dashboard():
    return build_dashboard()

@app.get("/api/v1/macro/indicators",response_model=list[Indicator])
def indicators():
    return build_dashboard().indicators

@app.get("/api/v1/sectors",response_model=list[Sector])
def sectors(market: Literal["ALL","US","KR"]="ALL"):
    return [s for s in build_dashboard().sectors if market=="ALL" or s.market==market]

@app.get("/api/v1/sectors/{sector_id}",response_model=Sector,responses={404:{"model":ApiError}})
def sector(sector_id:str,request:Request):
    return next((s for s in build_dashboard().sectors if s.id==sector_id),None) or not_found(request)

@app.get("/api/v1/relationships",response_model=list[Relationship])
def relationships():
    return build_dashboard().relationships

@app.get("/api/v1/relationships/{sector_id}",response_model=Relationship,responses={404:{"model":ApiError}})
def study(sector_id:str,request:Request,horizon:Horizon=Query(Horizon.TWENTY)):
    if not any(s.id==sector_id for s in build_dashboard().sectors):
        return not_found(request)
    return relationship(sector_id,horizon)

@app.get("/api/v1/learn/terms",response_model=list[Term])
def terms():
    return TERMS
