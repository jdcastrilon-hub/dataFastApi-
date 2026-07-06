from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_docum, repository_docum
from app.core.Services.ServiceInicializacion import repository_serviciosIni

router = APIRouter(
    prefix="/comercial/documentos",
    tags=["comercial - documentos"])

  