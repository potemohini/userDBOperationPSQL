from pydantic.main import BaseModel
from sqlalchemy.orm import Session
from src.db.alchemy import SessionLocal, Base
from src.utils.startup import init_all
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger
from sqlalchemy.orm import Session
from src.routes import get_db, get_raw_db
import psycopg2.extras

router = APIRouter()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

app = FastAPI()

class UpdateUserAddr(BaseModel):
    u_id:int
    u_addr: str
    u_is_deleted: int


@router.post("/address")
def add_address(
        u_id: int,
        u_addr:str,
        is_deleted: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Use parameterized query to prevent SQL injection
        insert_query = f"""
                  INSERT INTO address (u_id, u_addr, is_deleted)
                  VALUES ({u_id},'{u_addr}',{is_deleted});
              """
        cursor.execute(insert_query)
        rdb.commit()
        # Commit the transaction
        q  = f"""
            select * from address
        """
        cursor.execute(q)
        # Fetch the user_id from the returned result
        addr_id = cursor.fetchone()["a_id"]

        return {"message": "User created successfully", "addr_id": addr_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")



@router.get("/address/{u-id}")
def read_address_by_uid(
        u_id: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # query = f""" Select * from users"""
        query = f"""SELECT *FROM address WHERE u_id = {u_id};"""
        cursor.execute(query)
        result = cursor.fetchall()
        res = list(result)
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")


@router.get("/address/{a-id}")
def read_address_by_Addr_id(
        a_id: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # query = f""" Select * from users"""
        query = f"""SELECT *FROM address WHERE a_id = {a_id};"""
        cursor.execute(query)
        result = cursor.fetchall()
        res = list(result)
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/address/{u_id}")
def update_address(
        a_id:int,
        u_id: int,
        u_addr: str,
        is_deleted: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        update_query=f"""   UPDATE address SET u_id={u_id},u_addr = '{u_addr}',is_deleted={is_deleted} where a_id={a_id}"""

        cursor.execute(update_query)

        # Commit the transaction
        rdb.commit()
        q = f"""
                select * from address where a_id = {a_id}
        """
        cursor.execute(q)
        # Fetch the user_id from the returned result
        addr_id = cursor.fetchall()

        return {"message": "User created successfully", "addr_id": addr_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")



@router.delete("/address/{a_id}")
def delete_address_by_Addr_id(
    a_id: int,
    rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor()

        # Use a parameterized query to prevent SQL injection
        delete_query = """
            DELETE FROM address
            WHERE a_id = %s
        """
        cursor.execute(delete_query, (a_id,))

        # Check if any row was affected
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        rdb.commit()

        return {"message": "User deleted successfully"}
    except Exception as e:
        rdb.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    finally:
        cursor.close()