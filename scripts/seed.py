import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.user import User, get_hash
from app.models.service import Category, Festival, Service
from app.models.enquiry import Enquiry
from app.core.security import get_password_hash

async def seed():
    async with AsyncSessionLocal() as db:
        existing_admin = await db.get(User, 1)
        if not existing_admin:
            admin = User(
                phone_number="+919999999999",
                phone_number_hash=get_hash("+919999999999"),
                email="admin@mahalaxmipuja.com",
                email_hash=get_hash("admin@mahalaxmipuja.com"),
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_admin=True,
                is_active=True,
            )
            db.add(admin)
            print("Created admin user: +919999999999 / admin123")

        existing_categories = await db.execute(
            __import__("sqlalchemy").select(Category)
        )
        if not existing_categories.scalars().first():
            categories = [
                Category(name="Puja", slug="puja", description="Sacred puja ceremonies"),
                Category(name="Havan", slug="havan", description="Fire rituals"),
                Category(name="Festival Special", slug="festival-special", description="Festival-specific services"),
            ]
            db.add_all(categories)
            await db.flush()

            festivals = [
                Festival(name="Diwali"), Festival(name="Navratri"),
                Festival(name="Ganesh Chaturthi"), Festival(name="Durga Puja"),
            ]
            db.add_all(festivals)
            await db.flush()

            services = [
                Service(name="Lakshmi Puja", slug="lakshmi-puja", category_id=categories[0].id,
                        price=1100, description="Puja for Goddess Lakshmi", short_description="Wealth & prosperity puja",
                        icon=" Lakshmi", inclusions="Sankalp, 108 names recitation, aarti, prasad"),
                Service(name="Maha Lakshmi Havan", slug="maha-lakshmi-havan", category_id=categories[1].id,
                        price=2100, description="Havan for Maha Lakshmi", short_description="Fire ritual for abundance",
                        icon="🔥", inclusions="Sankalp, havan kund, aarti, prasad"),
                Service(name="Diwali Special Puja", slug="diwali-special-puja", category_id=categories[2].id,
                        price=5100, description="Special puja on Diwali", short_description="Diwali blessings", festivals=[festivals[0]]),
            ]
            db.add_all(services)
            print("Seeded categories, festivals, and services")

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
