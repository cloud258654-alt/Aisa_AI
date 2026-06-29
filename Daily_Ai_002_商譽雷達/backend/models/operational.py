from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Date, Boolean, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class OperationalMetric(Base):
    __tablename__ = "operational_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="pos_sales|order_volume|store_traffic|staff_count|inventory_status|promotion_active|complaint_tickets|service_capacity",
    )
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Real-time operational metrics recorded per store"},
    )


class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    staff_count: Mapped[int] = mapped_column(Integer, nullable=False)
    peak_hour_start: Mapped[Optional[time]] = mapped_column(String(5), nullable=True)
    peak_hour_end: Mapped[Optional[time]] = mapped_column(String(5), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Staff shift schedules for each store"},
    )


class StoreTraffic(Base):
    __tablename__ = "store_traffic"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    hour: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    visitor_count: Mapped[int] = mapped_column(Integer, nullable=False)
    peak_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weather_condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Hourly store traffic data"},
    )


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    item_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stock_level: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Inventory stock level snapshots per category"},
    )


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(50), nullable=False)
    store_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    discount_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Active and historical marketing campaigns"},
    )
