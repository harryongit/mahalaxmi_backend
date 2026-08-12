import random
import string
from math import ceil
from datetime import datetime
from typing import Any, Tuple
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

def generate_order_id() -> str:
    """Generate order ID in format MLX-YYYYMMDD-XXXX"""
    date_str = datetime.utcnow().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"MLX-{date_str}-{random_str}"

def paginate(page: int = 1, per_page: int = 20) -> Tuple[int, int]:
    return (page - 1) * per_page, per_page

async def paginated_query(db: AsyncSession, stmt: Select, page: int = 1, per_page: int = 20) -> dict:
    offset, limit = paginate(page, per_page)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    result = await db.execute(stmt.offset(offset).limit(limit))
    items = result.scalars().all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if per_page > 0 else 0,
    }
