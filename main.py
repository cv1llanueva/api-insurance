from fastapi import FastAPI, HTTPException, status
from typing import List
from fastapi import Query
import mysql.connector
import schemas
import random
import uuid
import datetime

app = FastAPI()

host_name = "52.2.83.96"  # Agrega el nombre del host de la base de datos
port_number = "8005"  # Agrega el número de puerto de la base de datos
user_name = "root"
password_db = "utec"
database_name = "bd_api_insurance"  # Modifica el nombre de la base de datos

# Conexión a la base de datos
def connect_to_db():
    return mysql.connector.connect(
        host=host_name,
        port=port_number,
        user=user_name,
        password=password_db,
        database=database_name
    )
# Definir la conexión a la base de datos (mismo código que antes)

@app.post("/api/v1/claims", response_model=schemas.ClaimOutput, status_code=status.HTTP_201_CREATED)
def create_claim(claim: schemas.ClaimCreate):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()

        # Verificar que la póliza asociada al reclamo existe y está activa
        cursor.execute("SELECT status FROM Policy WHERE policyId = %s", (claim.policyId,))
        policy_status = cursor.fetchone()
        if policy_status is None or policy_status[0] != 'active':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive policy")

        # Insertar el reclamo en la base de datos
        cursor.execute("INSERT INTO Claim (policyId, claimDate, description, status) VALUES (%s, %s, %s, %s)",
                       (claim.policyId, claim.claimDate, claim.description, 'submitted'))
        mydb.commit()

        # Obtener el ID del reclamo recién insertado
        claim_id = cursor.lastrowid

        # Crear la respuesta con el reclamo creado
        claim_output = schemas.ClaimOutput(
            claimId=claim_id,
            policyId=claim.policyId,
            claimDate=claim.claimDate,
            description=claim.description,
            status='submitted'
        )

        return claim_output

    except mysql.connector.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if 'mydb' in locals():
            mydb.close()

@app.get("/api/v1/claims", response_model=List[schemas.ClaimOutput])
def get_claims():
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()

        cursor.execute("""SELECT claimId, policyId, claimDate, description, status FROM Claim""")
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No claims found")

        claims = [schemas.ClaimOutput(
            claimId=claim[0],
            policyId=claim[1],
            claimDate=claim[2],
            description=claim[3],
            status=claim[4]
        ) for claim in result]

        return claims

    except mysql.connector.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if 'mydb' in locals():
            mydb.close()

@app.delete("/api/v1/claims/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(claim_id: int):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()

        # Verificar si el reclamo existe
        cursor.execute("SELECT status FROM Claim WHERE claimId = %s", (claim_id,))
        claim_status = cursor.fetchone()
        if claim_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

        # Eliminar el reclamo de la base de datos
        cursor.execute("DELETE FROM Claim WHERE claimId = %s", (claim_id,))
        mydb.commit()

    except mysql.connector.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if 'mydb' in locals():
            mydb.close()
