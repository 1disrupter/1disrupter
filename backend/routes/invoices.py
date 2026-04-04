"""
Invoice Generation — PDF invoices for subscription payments.
Generates on-demand, stores metadata in DB, serves downloadable PDFs.
"""
import os
import io
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import logging

from database import db
from routes.auth import get_current_user

logger = logging.getLogger("AlphaAI.Invoices")
router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

invoices_col = db["invoices"]
transactions_col = db["payment_transactions"]
users_col = db["users"]


@router.get("")
async def list_invoices(user: dict = Depends(get_current_user)):
    """List all invoices for the current user."""
    items = await invoices_col.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"invoices": items, "count": len(items)}


@router.post("/generate/{transaction_id}")
async def generate_invoice(transaction_id: str, user: dict = Depends(get_current_user)):
    """Generate a PDF invoice for a specific transaction."""
    # Check if invoice already exists
    existing = await invoices_col.find_one(
        {"transaction_id": transaction_id, "user_id": user["id"]}, {"_id": 0}
    )
    if existing:
        return {"invoice": existing, "message": "Invoice already exists"}

    # Find the transaction
    txn = await transactions_col.find_one(
        {"id": transaction_id, "user_id": user["id"]}, {"_id": 0}
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    now = datetime.now(timezone.utc)
    invoice_number = f"INV-{now.strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

    invoice = {
        "id": str(uuid.uuid4()),
        "invoice_number": invoice_number,
        "user_id": user["id"],
        "user_email": user.get("email", ""),
        "user_name": user.get("name", ""),
        "transaction_id": transaction_id,
        "strategy_name": txn.get("strategy_name", "AlphaAI Subscription"),
        "amount": txn.get("amount", 0),
        "currency": txn.get("currency", "usd").upper(),
        "payment_status": txn.get("payment_status", "paid"),
        "created_at": now.isoformat(),
        "transaction_date": txn.get("created_at", now.isoformat()),
    }

    await invoices_col.insert_one(invoice)
    logger.info(f"Invoice {invoice_number} generated for {user['email']}")

    return {"invoice": {k: v for k, v in invoice.items() if k != "_id"}, "message": "Invoice generated"}


@router.get("/download/{invoice_id}")
async def download_invoice(invoice_id: str, user: dict = Depends(get_current_user)):
    """Download a PDF invoice."""
    inv = await invoices_col.find_one(
        {"id": invoice_id, "user_id": user["id"]}, {"_id": 0}
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    pdf_buffer = _generate_pdf(inv)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{inv["invoice_number"]}.pdf"'
        },
    )


def _generate_pdf(inv: dict) -> io.BytesIO:
    """Generate a branded PDF invoice."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Colors
    bg = HexColor("#0A0A0A")
    purple = HexColor("#7B61FF")
    green = HexColor("#00FF94")
    white = HexColor("#FFFFFF")
    gray = HexColor("#A0A0A0")
    dark_gray = HexColor("#333333")

    # Background
    c.setFillColor(bg)
    c.rect(0, 0, w, h, fill=1)

    # Header bar
    c.setFillColor(purple)
    c.rect(0, h - 80, w, 80, fill=1)

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(white)
    c.drawString(30, h - 50, "Alpha AI")

    c.setFont("Helvetica", 11)
    c.drawString(30, h - 70, "AI-Powered Crypto Strategies")

    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(w - 30, h - 50, "INVOICE")

    c.setFont("Helvetica", 10)
    c.drawRightString(w - 30, h - 70, inv.get("invoice_number", ""))

    # Invoice details
    y = h - 120
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(white)
    c.drawString(30, y, "Bill To:")
    y -= 18
    c.setFont("Helvetica", 10)
    c.setFillColor(gray)
    c.drawString(30, y, inv.get("user_name", "Customer"))
    y -= 15
    c.drawString(30, y, inv.get("user_email", ""))

    # Date info on right
    y_right = h - 120
    c.setFont("Helvetica", 10)
    c.setFillColor(gray)
    c.drawRightString(w - 30, y_right, f"Date: {inv.get('created_at', '')[:10]}")
    y_right -= 18
    c.drawRightString(w - 30, y_right, f"Status: {inv.get('payment_status', 'paid').upper()}")

    # Divider
    y -= 40
    c.setStrokeColor(dark_gray)
    c.setLineWidth(0.5)
    c.line(30, y, w - 30, y)

    # Table header
    y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(purple)
    c.drawString(30, y, "DESCRIPTION")
    c.drawRightString(w - 30, y, "AMOUNT")

    # Divider
    y -= 8
    c.setStrokeColor(dark_gray)
    c.line(30, y, w - 30, y)

    # Line item
    y -= 22
    c.setFont("Helvetica", 10)
    c.setFillColor(white)
    c.drawString(30, y, inv.get("strategy_name", "AlphaAI Subscription"))

    amount = inv.get("amount", 0)
    currency = inv.get("currency", "USD")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(green)
    c.drawRightString(w - 30, y, f"${amount:.2f} {currency}")

    # Total
    y -= 40
    c.setStrokeColor(dark_gray)
    c.line(30, y, w - 30, y)
    y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(white)
    c.drawString(30, y, "TOTAL")
    c.setFillColor(green)
    c.drawRightString(w - 30, y, f"${amount:.2f} {currency}")

    # Footer
    y = 60
    c.setFont("Helvetica", 8)
    c.setFillColor(gray)
    c.drawCentredString(w / 2, y, "Alpha AI - AI-Powered Crypto Strategies")
    c.drawCentredString(w / 2, y - 12, "support@my-alpha-ai.com | https://my-alpha-ai.com")
    c.drawCentredString(w / 2, y - 24, "This is a computer-generated invoice. No signature required.")

    c.save()
    buf.seek(0)
    return buf
