from datetime import datetime, date
from sqlite3 import Date
from typing import List, Optional

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


class UserCreate(BaseModel):
    u_name: str
    u_dob: str


class UserResponse(UserCreate):
    u_id: int
    is_deleted: bool


# @app.post("/users/", response_model=UserResponse)
# def create_user(user: UserCreate):
#     db = SessionLocal()
#     db_user = User(**user.dict())
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user




class UpdateUserData(BaseModel):
    u_name: str
    u_dob: date
    u_is_deleted: int


@router.get("/users/{u-id}")
def read_users_by_uid(
        u_id: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # query = f""" Select * from users"""
        query = f"""SELECT *FROM users WHERE u_id = {u_id};"""
        cursor.execute(query)
        result = cursor.fetchall()
        res = list(result)
        return res
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")



@router.post("/users")
def create_user(
        u_name: str,
        u_dob: date,
        u_is_deleted: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Use parameterized query to prevent SQL injection
        insert_query = """
                  INSERT INTO users (name, dob, is_deleted)
                  VALUES (%s, %s, %s) RETURNING u_id
              """
        cursor.execute(insert_query, (u_name, u_dob, u_is_deleted))

        # Commit the transaction
        rdb.commit()

        # Fetch the user_id from the returned result
        user_id = cursor.fetchone()["u_id"]

        return {"message": "User created successfully", "user_id": user_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@router.get("/users")
def read_all_users(
    rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Use a parameterized query to prevent SQL injection
        select_query = """
            SELECT * FROM users
        """
        cursor.execute(select_query)

        # Fetch all users from the result
        users = cursor.fetchall()

        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@router.post("/users/{u_id}")
def update_user(
        u_id: int,
        u_name: str,
        u_dob: date,
        u_is_deleted: int,
        rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        update_query=f"""   UPDATE users SET name = '{u_name}', dob = '{u_dob}', is_deleted={u_is_deleted} where u_id={u_id}"""

        cursor.execute(update_query)

        # Commit the transaction
        rdb.commit()
        q = f"""
                select * from users where u_id = {u_id}
        """
        cursor.execute(q)
        # Fetch the user_id from the returned result
        user_id = cursor.fetchall()

        return {"message": "User created successfully", "user_id": user_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.debug(f"{e}")
        raise HTTPException(status_code=500, detail=f"{e}")


@router.delete("/users/{u_id}")
def delete_user_by_id(
    u_id: int,
    rdb: Session = Depends(get_raw_db)
):
    try:
        cursor = rdb.cursor()

        # Use a parameterized query to prevent SQL injection
        delete_query = """
            DELETE FROM users
            WHERE u_id = %s
        """
        cursor.execute(delete_query, (u_id,))

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