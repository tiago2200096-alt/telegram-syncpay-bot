import aiosqlite
from dataclasses import dataclass
from typing import Optional

DB_PATH = "app.db"

@dataclass
class Order:
    id: int
    user_id: int
    plan: str
    amount_cents: int
    sync_identifier: str
    status: str
    created_at: str

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            sync_identifier TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """)
        await db.commit()

async def create_order(user_id: int, plan: str, amount_cents: int, sync_identifier: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, plan, amount_cents, sync_identifier, status) VALUES (?,?,?,?, 'pending')",
            (user_id, plan, amount_cents, sync_identifier)
        )
        await db.commit()
        return cur.lastrowid

async def get_order(order_id: int) -> Optional[Order]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id,user_id,plan,amount_cents,sync_identifier,status,created_at FROM orders WHERE id=?",
            (order_id,)
        )
        row = await cur.fetchone()
        if not row:
            return None
        return Order(*row)

async def set_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()
                         
