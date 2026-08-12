"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- enums ---
    sa.Enum("RAKSHASA", "MANUSHYA", "DEVA", name="ganenum").create(op.get_bind())
    sa.Enum("PENDING", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="orderstatus").create(op.get_bind())
    sa.Enum("PENDING", "PAID", "FAILED", "REFUNDED", name="paymentstatus").create(op.get_bind())
    sa.Enum("FRONTEND_VERIFIED", "WEBHOOK_VERIFIED", "MANUAL_VERIFIED", name="paymentverificationsource").create(op.get_bind())
    sa.Enum("OPEN", "IN_PROGRESS", "RESOLVED", name="enquirystatus").create(op.get_bind())

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("phone_number_hash", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("email_hash", sa.String(64), unique=True, index=True, nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.Text(), nullable=False),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("gotra", sa.String(50), nullable=True),
        sa.Column("gan", sa.Enum("RAKSHASA", "MANUSHYA", "DEVA", name="ganenum"), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(50), nullable=True),
        sa.Column("state", sa.String(50), nullable=True),
        sa.Column("pin_code", sa.String(20), nullable=True),
        sa.Column("country", sa.String(50), nullable=True),
        sa.Column("is_admin", sa.Boolean(), default=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("whatsapp_opt_in", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # --- categories ---
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("slug", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # --- festivals ---
    op.create_table(
        "festivals",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), unique=True, index=True, nullable=False),
    )

    # --- services ---
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), unique=True, index=True, nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("short_description", sa.String(255), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("is_custom_amount", sa.Boolean(), default=False),
        sa.Column("min_amount", sa.Integer(), nullable=True),
        sa.Column("active_from", sa.Date(), nullable=True),
        sa.Column("active_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("display_order", sa.Integer(), default=0),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("inclusions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- service <-> festival association ---
    op.create_table(
        "service_festival",
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), primary_key=True),
        sa.Column("festival_id", sa.Integer(), sa.ForeignKey("festivals.id"), primary_key=True),
    )

    # --- orders ---
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("order_id", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="orderstatus"), default="PENDING"),
        sa.Column("payment_status", sa.Enum("PENDING", "PAID", "FAILED", "REFUNDED", name="paymentstatus"), default="PENDING"),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("booking_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # --- order_items ---
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("devotee_name", sa.String(100), nullable=True),
        sa.Column("gotra", sa.String(50), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), default="PENDING"),
    )

    # --- payments ---
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), unique=True, nullable=False),
        sa.Column("razorpay_order_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("razorpay_payment_id", sa.String(100), unique=True, index=True, nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), default="PENDING"),
        sa.Column("verification_source", sa.Enum("FRONTEND_VERIFIED", "WEBHOOK_VERIFIED", "MANUAL_VERIFIED", name="paymentverificationsource"), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=True),
    )

    # --- enquiries ---
    op.create_table(
        "enquiries",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("OPEN", "IN_PROGRESS", "RESOLVED", name="enquirystatus"), default="OPEN"),
        sa.Column("admin_reply", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("enquiries")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("service_festival")
    op.drop_table("services")
    op.drop_table("festivals")
    op.drop_table("categories")
    op.drop_table("users")

    sa.Enum(name="enquirystatus").drop(op.get_bind())
    sa.Enum(name="paymentverificationsource").drop(op.get_bind())
    sa.Enum(name="paymentstatus").drop(op.get_bind())
    sa.Enum(name="orderstatus").drop(op.get_bind())
    sa.Enum(name="ganenum").drop(op.get_bind())
