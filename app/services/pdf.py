from weasyprint import HTML
import tempfile
from app.models.order import Order

def generate_invoice_pdf(order: Order, user_name: str) -> str:
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .details {{ margin-bottom: 20px; }}
                .items table {{ width: 100%; border-collapse: collapse; }}
                .items th, .items td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .total {{ font-weight: bold; text-align: right; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>MahalaxmiPuja.com - Invoice</h2>
            </div>
            <div class="details">
                <p><strong>Order ID:</strong> {order.order_id}</p>
                <p><strong>Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else ''}</p>
                <p><strong>Customer:</strong> {user_name}</p>
                <p><strong>Payment Status:</strong> {order.payment_status.value}</p>
            </div>
            <div class="items">
                <table>
                    <tr>
                        <th>Service</th>
                        <th>Devotee Name</th>
                        <th>Amount (INR)</th>
                    </tr>
                    {"".join(
                        f"<tr><td>{item.service.name if item.service else 'Custom'}</td><td>{item.devotee_name or ''}</td><td>{item.amount / 100:.2f}</td></tr>"
                        for item in order.items
                    )}
                </table>
            </div>
            <div class="total">
                <p>Total Amount: INR {order.total_amount / 100:.2f}</p>
            </div>
        </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return tmp.name
