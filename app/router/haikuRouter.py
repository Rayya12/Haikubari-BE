from fastapi import APIRouter, Depends, HTTPException,Query
from app.users import current_verified_user
from app.schema.haikuSchema import HaikuPost
from app.model.db import Haiku, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select,func,asc,desc



router = APIRouter(prefix="/haikus", tags=["haiku"])

@router.post("/create")
async def createHaiku(haiku:HaikuPost,user=Depends(current_verified_user),session: AsyncSession = Depends(get_async_session)):
    new_haiku = Haiku(**haiku.model_dump(), user_id=user.id)
    session.add(new_haiku)
    await session.commit()
    await session.refresh(new_haiku)
    return {
        "ok":True,
        "haiku":new_haiku
}

PAGE_SIZE_DEFAULT = 8
PAGE_SIZE_MAX = 30

@router.get("/")
async def get_all_haiku(session:AsyncSession = Depends(get_async_session),user=Depends(current_verified_user),
                        page:int = Query(1,ge=1),
                        page_size:int = Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX),
                        q:str | None = Query(None,description="俳句を探す"),
                        sort:str = Query("created_at",regex="^(created_at|likes)$"),
                        order:str = Query("desc",regex="^(asc|desc)$")):
    
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通ユーザー以外はできません")
    
    offset = (page-1)*page_size
    
    condition = []
    
    if q:
        condition.append(or_(Haiku.title.ilike(f"%{q}%"),
                             Haiku.shimogo.ilike(f"%{q}%"),
                             Haiku.nakasichi.ilike(f"%{q}%"),
                             Haiku.shimogo.ilike(f"%{q}%")))
        
        sort_map = {
            "created_at":Haiku.created_at,
            "likes":Haiku.likes
        }
        
        sort_columns = sort_map.get(sort)
        order_fn = desc if order == "desc" else asc
        
        total = await session.scalar(select(func.count()).select_from(Haiku).where(*condition))
        
        stmt = (select(Haiku).where(*condition).order_by(order_fn(sort_columns)).offset(offset).limit(page_size))
        
        result = await session.execute(stmt)
        items = result.scalars().all()
        
        return ({
            "page":page,
            "page_size":page_size,
            "q":q,
            "sort":sort,
            "total":total,
            "order":order,
            "total_pages" : (total+page_size-1) // page_size if total else 0,
            "items" : items
        })



@router.get("/my-haikus")
async def  get_haiku_from_id_for_page(session : AsyncSession = Depends(get_async_session),user=Depends(current_verified_user),
                                      page:int = Query(1,ge=1),
                                      page_size: int = Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX),
                                      q:str | None =Query(None,description="俳句を探す"),
                                      sort: str = Query("created_at", regex="^(created_at|likes)$"),
                                      order: str = Query("desc", regex="^(asc|desc)$"),):
    
    id = user.id
    
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通役しか使えません")
    
    # offset untuk page 1 = 0, page 2 = 6, dst
    offset = (page - 1)*page_size
    
    conditions = [Haiku.user_id == id]
    
    if q:
        conditions.append(or_(Haiku.hashigo.ilike(f"%{q}%"),
        Haiku.nakasichi.ilike(f"%{q}%"),
        Haiku.shimogo.ilike(f"%{q}%"),
        Haiku.title.ilike(f"%{q}%")))

    sort_map = {
        "created_at":Haiku.created_at,
        "likes":Haiku.likes
    }
    
    sort_column = sort_map.get(sort)
    order_fn = desc if order == "desc" else asc
    
    # total count
    total = await session.scalar(
        select(func.count()).select_from(Haiku).where(*conditions)
    )
    
    stmt = (select(Haiku).where(*conditions).order_by(order_fn(sort_column),Haiku.id).offset(offset).limit(page_size))
    
    result = await session.execute(stmt)
    items = result.scalars().all()
    
    return {
        "page": page,
        "page_size": page_size,
        "q": q,
        "sort": sort,
        "order": order,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
        "items": items,
    }
    
    

    
        
    
    
    
    
    
    