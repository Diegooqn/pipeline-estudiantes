import re
import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

VERSION = "1.0"

app = FastAPI(title="API Estudiantes", version=VERSION)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StudentIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    correo: str

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("correo electrónico inválido")
        return v


class Student(StudentIn):
    id: str


# Almacenamiento en memoria (igual que en la actividad 4)
STUDENTS: Dict[str, Student] = {}


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.post("/students", response_model=Student, status_code=201)
def crear_estudiante(data: StudentIn):
    if any(s.correo == data.correo for s in STUDENTS.values()):
        raise HTTPException(status_code=409, detail="Ya existe un estudiante con ese correo")
    student = Student(id=str(uuid.uuid4()), **data.model_dump())
    STUDENTS[student.id] = student
    return student


@app.get("/students/{student_id}", response_model=Student)
def obtener_estudiante(student_id: str):
    student = STUDENTS.get(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student


@app.get("/students", response_model=List[Student])
def listar_estudiantes():
    return list(STUDENTS.values())
