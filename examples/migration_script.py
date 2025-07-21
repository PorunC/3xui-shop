"""
数据库迁移脚本：从VPN订阅系统迁移到通用电子商品系统
执行步骤：
1. 备份现有数据
2. 创建新表结构
3. 迁移用户数据
4. 转换现有交易数据
5. 清理VPN相关数据
6. 插入示例产品数据
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 这些需要在实际实施时导入
# from app.config import load_config
# from app.db.models import User, Transaction
# from app.db.models.product import Product, Order, ProductCategory

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """数据库迁移工具类"""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def run_migration(self) -> bool:
        """执行完整的数据库迁移"""
        try:
            logger.info("开始数据库迁移...")
            
            # 1. 备份现有数据
            await self.backup_existing_data()
            
            # 2. 创建新表结构
            await self.create_new_tables()
            
            # 3. 迁移用户数据
            await self.migrate_user_data()
            
            # 4. 转换交易数据为订单数据
            await self.convert_transactions_to_orders()
            
            # 5. 清理VPN相关数据
            await self.cleanup_vpn_data()
            
            # 6. 插入示例产品数据
            await self.insert_sample_products()
            
            # 7. 更新序列和索引
            await self.update_sequences_and_indexes()
            
            logger.info("数据库迁移完成！")
            return True
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            await self.rollback_migration()
            return False
    
    async def backup_existing_data(self) -> None:
        """备份现有数据"""
        logger.info("备份现有数据...")
        
        async with self.session_factory() as session:
            # 备份用户数据
            users_result = await session.execute(text("SELECT * FROM users"))
            users_data = [dict(row) for row in users_result.fetchall()]
            
            # 备份交易数据
            transactions_result = await session.execute(text("SELECT * FROM transactions"))
            transactions_data = [dict(row) for row in transactions_result.fetchall()]
            
            # 备份服务器数据（将被删除）
            try:
                servers_result = await session.execute(text("SELECT * FROM servers"))
                servers_data = [dict(row) for row in servers_result.fetchall()]
            except:
                servers_data = []
            
            # 备份优惠码数据
            promocodes_result = await session.execute(text("SELECT * FROM promocodes"))
            promocodes_data = [dict(row) for row in promocodes_result.fetchall()]
            
            # 保存备份文件
            backup_data = {
                "backup_time": datetime.now().isoformat(),
                "users": users_data,
                "transactions": transactions_data, 
                "servers": servers_data,
                "promocodes": promocodes_data
            }
            
            backup_file = Path("migration_backup.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据备份完成: {backup_file}")
    
    async def create_new_tables(self) -> None:
        """创建新的表结构"""
        logger.info("创建新表结构...")
        
        async with self.session_factory() as session:
            # 创建产品分类表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS product_categories (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    name_en VARCHAR(100),
                    name_ru VARCHAR(100),
                    description TEXT,
                    icon VARCHAR(10),
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # 创建产品表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(100) NOT NULL,
                    price_data TEXT NOT NULL,
                    stock_quantity INTEGER DEFAULT -1,
                    is_active BOOLEAN DEFAULT TRUE,
                    delivery_type VARCHAR(50) DEFAULT 'digital',
                    delivery_config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建订单表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    duration VARCHAR(10) NOT NULL,
                    total_price REAL NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    payment_id VARCHAR(255),
                    delivery_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    delivered_at TIMESTAMP
                )
            """))
            
            await session.commit()
            logger.info("新表创建完成")
    
    async def migrate_user_data(self) -> None:
        """迁移用户数据，移除VPN相关字段"""
        logger.info("迁移用户数据...")
        
        async with self.session_factory() as session:
            # 创建新的用户表（没有VPN字段）
            await session.execute(text("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER UNIQUE NOT NULL,
                    first_name VARCHAR(32) NOT NULL,
                    username VARCHAR(32),
                    language_code VARCHAR(5) NOT NULL DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_trial_used BOOLEAN DEFAULT FALSE,
                    source_invite_name VARCHAR(100)
                )
            """))
            
            # 复制用户数据（排除VPN字段）
            await session.execute(text("""
                INSERT INTO users_new (
                    tg_id, first_name, username, language_code, 
                    created_at, is_trial_used, source_invite_name
                )
                SELECT 
                    tg_id, first_name, username, language_code,
                    created_at, is_trial_used, source_invite_name
                FROM users
            """))
            
            # 替换原表
            await session.execute(text("DROP TABLE users"))
            await session.execute(text("ALTER TABLE users_new RENAME TO users"))
            
            await session.commit()
            logger.info("用户数据迁移完成")
    
    async def convert_transactions_to_orders(self) -> None:
        """将交易记录转换为订单记录"""
        logger.info("转换交易数据为订单数据...")
        
        async with self.session_factory() as session:
            # 获取所有交易记录
            result = await session.execute(text("SELECT * FROM transactions"))
            transactions = result.fetchall()
            
            # 创建默认产品（用于转换现有交易）
            await session.execute(text("""
                INSERT OR IGNORE INTO products (
                    id, name, description, category, price_data,
                    delivery_type, is_active
                ) VALUES (
                    999, '历史VPN订阅', '从旧系统迁移的VPN订阅记录', 'legacy',
                    '{"RUB": {"30": 100, "90": 250, "180": 450, "365": 800}}',
                    'manual', TRUE
                )
            """))
            
            # 转换每个交易为订单
            for transaction in transactions:
                # 解析订阅信息以确定时长
                subscription_info = transaction.subscription
                duration = self._parse_duration_from_subscription(subscription_info)
                
                # 创建对应的订单记录
                await session.execute(text("""
                    INSERT INTO orders (
                        user_id, product_id, quantity, duration,
                        total_price, currency, status, payment_method,
                        created_at, paid_at, delivered_at
                    ) VALUES (
                        :user_id, 999, 1, :duration,
                        :price, :currency, 'delivered', 'legacy',
                        :created_at, :created_at, :created_at
                    )
                """), {
                    "user_id": transaction.tg_id,
                    "duration": duration,
                    "price": transaction.amount,
                    "currency": transaction.currency,
                    "created_at": transaction.created_at
                })
            
            await session.commit()
            logger.info(f"转换了 {len(transactions)} 条交易记录为订单")
    
    async def cleanup_vpn_data(self) -> None:
        """清理VPN相关数据"""
        logger.info("清理VPN相关数据...")
        
        async with self.session_factory() as session:
            # 删除服务器表
            try:
                await session.execute(text("DROP TABLE IF EXISTS servers"))
                logger.info("已删除servers表")
            except Exception as e:
                logger.warning(f"删除servers表时出错: {e}")
            
            # 可以选择保留transactions表作为历史记录，或者删除
            # await session.execute(text("DROP TABLE IF EXISTS transactions"))
            
            await session.commit()
            logger.info("VPN数据清理完成")
    
    async def insert_sample_products(self) -> None:
        """插入示例产品数据"""
        logger.info("插入示例产品数据...")
        
        # 读取产品配置文件
        products_file = Path("examples/products.json")
        if not products_file.exists():
            logger.warning("产品配置文件不存在，跳过示例数据插入")
            return
        
        try:
            with open(products_file, 'r', encoding='utf-8') as f:
                products_config = json.load(f)
        except Exception as e:
            logger.error(f"读取产品配置文件失败: {e}")
            return
        
        async with self.session_factory() as session:
            # 插入产品分类
            for category in products_config.get("categories", []):
                await session.execute(text("""
                    INSERT OR REPLACE INTO product_categories (
                        id, name, name_en, name_ru, description, icon, sort_order
                    ) VALUES (
                        :id, :name, :name_en, :name_ru, :description, :icon, :sort_order
                    )
                """), {
                    "id": category["id"],
                    "name": category["name"],
                    "name_en": category.get("name_en"),
                    "name_ru": category.get("name_ru"),
                    "description": category.get("description"),
                    "icon": category.get("icon"),
                    "sort_order": category.get("sort_order", 0)
                })
            
            # 插入产品数据
            for product in products_config.get("products", []):
                await session.execute(text("""
                    INSERT OR REPLACE INTO products (
                        id, name, description, category, price_data,
                        stock_quantity, is_active, delivery_type, delivery_config
                    ) VALUES (
                        :id, :name, :description, :category, :price_data,
                        :stock, :is_active, :delivery_type, :delivery_config
                    )
                """), {
                    "id": product["id"],
                    "name": product["name"],
                    "description": product["description"],
                    "category": product["category"],
                    "price_data": json.dumps(product["prices"]),
                    "stock": product.get("stock", -1),
                    "is_active": product.get("is_active", True),
                    "delivery_type": product.get("delivery_type", "digital"),
                    "delivery_config": json.dumps(product.get("delivery_config", {}))
                })
            
            await session.commit()
            logger.info(f"插入了 {len(products_config.get('products', []))} 个示例产品")
    
    async def update_sequences_and_indexes(self) -> None:
        """更新序列和创建索引"""
        logger.info("更新序列和索引...")
        
        async with self.session_factory() as session:
            # 为新表创建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
                "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
                "CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)",
            ]
            
            for index_sql in indexes:
                await session.execute(text(index_sql))
            
            await session.commit()
            logger.info("序列和索引更新完成")
    
    async def rollback_migration(self) -> None:
        """回滚迁移（如果可能）"""
        logger.warning("尝试回滚迁移...")
        
        # 这里可以实现回滚逻辑
        # 例如从备份文件恢复数据
        backup_file = Path("migration_backup.json")
        if backup_file.exists():
            logger.info("发现备份文件，可以手动恢复数据")
        else:
            logger.error("未找到备份文件，无法自动回滚")
    
    def _parse_duration_from_subscription(self, subscription: str) -> str:
        """从订阅信息中解析时长"""
        # 这里根据原来的订阅格式解析时长
        # 例如 "VPN-30days" -> "30"
        if "30" in subscription:
            return "30"
        elif "90" in subscription:
            return "90"
        elif "180" in subscription:
            return "180"
        elif "365" in subscription:
            return "365"
        else:
            return "30"  # 默认30天


class MigrationVerifier:
    """迁移验证工具"""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def verify_migration(self) -> bool:
        """验证迁移结果"""
        logger.info("验证迁移结果...")
        
        try:
            async with self.session_factory() as session:
                # 检查表是否存在
                tables_to_check = ['users', 'products', 'orders', 'product_categories']
                for table in tables_to_check:
                    result = await session.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                    ))
                    if not result.fetchone():
                        logger.error(f"表 {table} 不存在")
                        return False
                
                # 检查数据完整性
                user_count = await session.execute(text("SELECT COUNT(*) FROM users"))
                logger.info(f"用户数量: {user_count.scalar()}")
                
                product_count = await session.execute(text("SELECT COUNT(*) FROM products"))
                logger.info(f"产品数量: {product_count.scalar()}")
                
                order_count = await session.execute(text("SELECT COUNT(*) FROM orders"))
                logger.info(f"订单数量: {order_count.scalar()}")
                
                # 检查VPN表是否已删除
                servers_check = await session.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='servers'"
                ))
                if servers_check.fetchone():
                    logger.warning("servers表仍然存在，可能需要手动删除")
                
                logger.info("迁移验证通过！")
                return True
                
        except Exception as e:
            logger.error(f"迁移验证失败: {e}")
            return False


async def main():
    """主迁移函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 数据库连接（需要根据实际配置修改）
    database_url = "sqlite+aiosqlite:///./data/bot_database.db"
    
    # 执行迁移
    migrator = DatabaseMigrator(database_url)
    success = await migrator.run_migration()
    
    if success:
        # 验证迁移结果
        verifier = MigrationVerifier(database_url)
        verified = await verifier.verify_migration()
        
        if verified:
            print("🎉 数据库迁移完成并验证通过！")
            print("请检查以下内容：")
            print("1. 备份文件：migration_backup.json")
            print("2. 新的产品数据是否正确加载")
            print("3. 用户数据是否完整迁移")
            print("4. 订单转换是否正确")
        else:
            print("❌ 迁移验证失败，请检查日志")
    else:
        print("❌ 数据库迁移失败，请检查日志")


if __name__ == "__main__":
    asyncio.run(main())
