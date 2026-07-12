from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional


def siguiente_numerador(db: Session, id_emp: int, codigo: str) -> Optional[int]:
    """
    Devuelve el siguiente consecutivo para (id_emp, codigo), creando la fila la
    primera vez que se pide ese numerador para esa empresa.

    Si "requiere_consecutivo" está en False para esa empresa/tipo, no incrementa
    y devuelve None: el módulo que llama debe permitir entonces que el usuario
    ingrese el código manualmente.

    El incremento (UPDATE ... RETURNING) confirma su propio commit de inmediato,
    para no dejar la fila bloqueada mientras dure la transacción de quien llama
    (igual que se comportan las secuencias nativas de Postgres que ya usa el
    sistema en otros módulos): si la operación que pidió el número falla después,
    el consecutivo queda con un salto, pero nunca se repite ni bloquea a otro usuario.
    """
    # 1. Aseguramos que la fila exista (primera vez que se pide este numerador para la empresa)
    db.execute(text("""
        INSERT INTO md_numeradores (id_emp, codigo, ultimo_valor, requiere_consecutivo)
        VALUES (:id_emp, :codigo, 0, true)
        ON CONFLICT (id_emp, codigo) DO NOTHING
    """), {"id_emp": id_emp, "codigo": codigo})
    db.commit()

    # 2. Verificamos si esta empresa/tipo debe respetar el consecutivo
    requiere = db.execute(text("""
        SELECT requiere_consecutivo FROM md_numeradores
        WHERE id_emp = :id_emp AND codigo = :codigo
    """), {"id_emp": id_emp, "codigo": codigo}).scalar()

    if not requiere:
        return None

    # 3. Incremento atómico: el UPDATE toma el bloqueo de fila solo por esta instrucción
    nuevo_valor = db.execute(text("""
        UPDATE md_numeradores
        SET ultimo_valor = ultimo_valor + 1
        WHERE id_emp = :id_emp AND codigo = :codigo
        RETURNING ultimo_valor
    """), {"id_emp": id_emp, "codigo": codigo}).scalar()
    db.commit()

    return nuevo_valor


def formatear_numerador(valor: int, longitud: int = 6) -> str:
    """Aplica el padding de ceros, ej. 123 -> '000123'."""
    return str(valor).zfill(longitud)
