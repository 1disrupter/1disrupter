from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

from app.core.database import Base


class UserWallet(Base):
    __tablename__ = "user_wallets"

    user_id = Column(String, primary_key=True, index=True)
    credits = Column(Integer, default=0)

    # 🔥 REQUIRED FOR YOUR ROUTE
    referral_credits = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)
