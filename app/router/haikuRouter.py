from fastapi import APIRouter, Depends, HTTPException,Query
from app.users import current_verified_user
from app.schema.haikuSchema import HaikuPost
from app.model.db import Haiku, get_async_session,Like
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select,func,asc,desc
from uuid import UUID
from app.core.dependencies import current_active_watcher
from sqlalchemy.orm import selectinload



router = APIRouter(prefix="/haikus", tags=["haiku"])

@router.post("/create")
async def createHaiku(haiku:HaikuPost,user=Depends(current_verified_user),session: AsyncSession = Depends(get_async_session)):
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通役しか使えません")
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
                             Haiku.hashigo.ilike(f"%{q}%"),
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
    
    
@router.get("/{id}")
async def get_haiku_with_id(id :str,session:AsyncSession = Depends(get_async_session),user=Depends(current_verified_user)):
    if not user.role == "common":
        raise HTTPException(status_code=403,detail="普通役しか使えません")
    
    result = await session.scalar(select(Haiku).options(selectinload(Haiku.user)).where(Haiku.id == id))
    if not result:
        raise HTTPException(status_code=404, detail="俳句が見つかりません")

    return {
        "haiku" : result,
        "user" : result.user,
        "isMine" : result.user_id == user.id
    }

@router.patch("/{id}/likes")
async def likesHaiku(id:str,user = Depends(current_verified_user),session:AsyncSession = Depends(get_async_session)):
    
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="まだログインしませんね、ログインしてください")
    
    new_like = Like(user_id = user.id,haiku_id = id)
    try:
        session.add(new_like)
        await session.commit()
        await session.refresh(new_like)
    except Exception:
        raise HTTPException(status_code=400,detail="いいねすることができません")
        
    
    
    result = await session.scalar(select(Haiku).where(Haiku.id == id))
    result.likes = result.likes + 1
    
    session.add(result)
    await session.commit()
    await session.refresh(result)
    
    return {
        "ok":True,
        "result":result
    }
    
@router.delete("/{id}/unlikes")
async def unlikesHaiku(
    id: str,
    user=Depends(current_verified_user),
    session: AsyncSession = Depends(get_async_session),
):
    if user.role != "common":
        raise HTTPException(status_code=403, detail="まだログインしませんね、ログインしてください")

    like_obj = await session.scalar(
        select(Like).where(Like.user_id == user.id, Like.haiku_id == id)
    )
    haiku = await session.scalar(select(Haiku).where(Haiku.id == id))

    if not haiku:
        raise HTTPException(status_code=404, detail="俳句が見つかりません")

    if not like_obj:
        raise HTTPException(status_code=404, detail="いいねが見つかりません")

    if haiku.likes <= 0:
        raise HTTPException(status_code=400, detail="いいね回数はゼロ以下はできません")

    haiku.likes -= 1
    await session.delete(like_obj)   # no await

    await session.commit()
    await session.refresh(haiku)

    return {"ok": True, "result": haiku}


@router.patch("/{id}/edit")
async def editHaiku(id:UUID,hakupost:HaikuPost,session:AsyncSession=Depends(get_async_session),user = Depends(current_verified_user)):
    if not (user.role == "common"):
        raise HTTPException(status_code=403,detail="普通の役しか使いません")
    
    haiku = await session.scalar(select(Haiku).where(Haiku.id == id))
    
    if not haiku:
        raise HTTPException(status_code=404,detail= "探している俳句は見つかりません")
    
    if haiku.user_id != user.id:
        raise HTTPException(status_code=400,detail="これはあなたの俳句ではありませんね")
    
    haiku.title = hakupost.title
    haiku.shimogo = hakupost.shimogo
    haiku.nakasichi = hakupost.nakasichi
    haiku.hashigo = hakupost.hashigo
    haiku.description = hakupost.description
    
    await session.commit()
    await session.refresh(haiku)
    
    return haiku

@router.delete("/{id}")
async def deleteHaiku(id:UUID,session:AsyncSession = Depends(get_async_session),user=Depends(current_verified_user)):
    if not user.role == "common":
        raise HTTPException(status_code=403,detail="普通の役しか使得ません")
    
    
    selectedHaiku = await session.scalar(select(Haiku).where(Haiku.id == id))
    
    if not selectedHaiku:
        raise HTTPException(status_code=404,detail="俳句が見つかりませんでした")
    
    if selectedHaiku.user_id != user.id:
        raise HTTPException(status_code=403,detail="これはあなたの俳句ではありませんね")
    
    await session.delete(selectedHaiku)
    await session.commit()

    return {
        "ok":True
    }
    
    
@router.get("/all/like")
async def getAllWithLike(session : AsyncSession = Depends(get_async_session), user = Depends(current_active_watcher), sort: str = Query("desc",regex="^(asc|desc)$")):
    if not user.role == "watcher":
        raise HTTPException(status_code=403,detail="普通の役はこの機能を使えません")
    if not user.status == "pending":
        raise HTTPException(status_code=403,detail="まだアドミンに肯定されません、また後程お待ちください")
    if not user.status == "rejected":
        raise HTTPException(status_code=403,detail="あなたのアカウントは、拒否されます、お詳しいことは、アドミンに申し込んでください")
    
    sort_order = desc if sort == "desc" else asc
    
    response = await session.execute(select(Haiku).order_by(Haiku.likes(sort_order)))
    
    items = response.scalars().all()
    
    listTitleAndLike = []
    for item in items:
        listTitleAndLike.append((item.title,item.likes))
        
    
    return {
        "titleAndLikes" : listTitleAndLike
    }
    
    
    
    
    
    
        
    
    
    
    




    
    

    
        
    
    
    
    
    
    