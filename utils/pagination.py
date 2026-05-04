from typing import Any, Dict
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate_query(
    session: AsyncSession,
    model: Any,
    offset: int = 0,
    limit: int = 100,
    order_by: Any = None,
    base_url: str = "/",
) -> Dict:
    count_result = await session.execute(select(func.count()).select_from(model))
    total_count = count_result.scalar()

    query = select(model).offset(offset).limit(limit)
    if order_by is not None:
        query = query.order_by(order_by)

    result = await session.execute(query)
    items = result.scalars().all()

    next_offset = offset + limit if offset + limit < total_count else None
    prev_offset = offset - limit if offset - limit >= 0 else None

    links = {}
    if next_offset is not None:
        links["next"] = f"{base_url}?offset={next_offset}&limit={limit}"
    if prev_offset is not None:
        links["previous"] = f"{base_url}?offset={prev_offset}&limit={limit}"

    return {
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "items": items,
        "links": links,
    }
