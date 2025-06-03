from flask import Flask, render_template, request, session, redirect, url_for, send_file
from flask_session import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import pymysql
import os

app = Flask(__name__, template_folder='template')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'fri108_cvman',
    'charset': 'utf8mb4'
}

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'
Session(app)

def get_db_connection():
    """Create database connection"""
    return pymysql.connect(**DB_CONFIG)

def check_role_access(required_role):
    """Check if user has required role access"""
    if 'username' not in session:
        return False
    if 'role' not in session:
        return False
    return session.get('role') == required_role

@app.route('/')
def index():
    if 'username' in session and 'role' in session:
        return redirect(url_for('home'))
    elif 'username' in session:
        return redirect(url_for('role_selection'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication (in production, use proper authentication)
        if username and password:  # Add your authentication logic here
            session['username'] = username
            session['password'] = password
            return redirect(url_for('role_selection'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/role')
def role_selection():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # If role already selected, go to home
    if 'role' in session:
        return redirect(url_for('home'))
    
    return render_template('role.html')

@app.route('/select_role', methods=['POST'])
def select_role():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    role = request.form.get('role')
    if role:
        session['role'] = role
        return redirect(url_for('home'))
    
    return redirect(url_for('role_selection'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Main home route - redirects based on role
@app.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_home'))
    elif role == 'Finance Staff':
        return redirect(url_for('finance_home'))
    elif role == 'Warehouse Staff':
        return redirect(url_for('warehouse_home'))
    elif role == 'Procurement Staff':
        return redirect(url_for('procurement_home'))
    else:
        return redirect(url_for('role_selection'))

# ==================== PRODUCTION STAFF ROUTES ====================

@app.route("/production/home")
def production_home():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
            
            # Calculate statistics
            make_items = [m for m in data if m[7] == 'Make']
            buy_items = [m for m in data if m[7] == 'Buy']
            low_stock_items = [m for m in data if m[6] < 5]  # assuming 5 is low stock threshold
            
    finally:
        connection.close()
    
    return render_template('production/home.html', 
                         material=data,
                         make_items_count=len(make_items),
                         buy_items_count=len(buy_items),
                         low_stock_count=len(low_stock_items))


# ==================== FINANCE STAFF ROUTES ====================

@app.route("/finance/home")
def finance_home():
    if not check_role_access('Finance Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
            
            # Calculate financial metrics
            total_materials = len(data)
            total_stock_value = sum([m[6] for m in data])  # Assuming stok represents value
            high_value_items = [m for m in data if m[6] > 100]  # High value threshold
            
    finally:
        connection.close()
    
    return render_template('finance/home.html', 
                         material=data,
                         total_materials=total_materials,
                         total_stock_value=total_stock_value,
                         high_value_items_count=len(high_value_items))

@app.route("/finance/reports")
def finance_reports():
    if not check_role_access('Finance Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('finance/reports.html', material=data)

@app.route("/finance/cost-analysis")
def finance_cost_analysis():
    if not check_role_access('Finance Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('finance/cost_analysis.html', material=data)

@app.route("/finance/budget")
def finance_budget():
    if not check_role_access('Finance Staff'):
        return redirect(url_for('login'))
    
    return render_template('finance/budget_planning.html')

@app.route('/finance/download-report')
def download_finance_report():
    if not check_role_access('Finance Staff'):
        return redirect(url_for('login'))
    
    pdf_path = os.path.join(DOWNLOAD_FOLDER, f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_report_pdf(pdf_path, 'Finance')
    return send_file(pdf_path, as_attachment=True, download_name="finance_report.pdf")

# ==================== WAREHOUSE STAFF ROUTES ====================

@app.route("/warehouse/home")
def warehouse_home():
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
            
            # Calculate warehouse metrics
            total_items = len(data)
            total_stock = sum([m[6] for m in data])
            zero_stock_items = [m for m in data if m[6] == 0]
            low_stock_items = [m for m in data if m[6] > 0 and m[6] < 10]
            
    finally:
        connection.close()
    
    return render_template('warehouse/home.html', 
                         material=data,
                         total_items=total_items,
                         total_stock=total_stock,
                         zero_stock_count=len(zero_stock_items),
                         low_stock_count=len(low_stock_items))

@app.route("/warehouse/inventory")
def warehouse_inventory():
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('warehouse/inventory.html', material=data)

@app.route("/warehouse/stock-movement")
def warehouse_stock_movement():
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    return render_template('warehouse/stock_movement.html')

@app.route("/warehouse/receiving")
def warehouse_receiving():
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    return render_template('warehouse/receiving.html')

@app.route('/warehouse/update-stock/<int:id>', methods=['GET', 'POST'])
def warehouse_update_stock(id):
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_stok = request.form['stok']
        movement_type = request.form.get('movement_type', 'adjustment')
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE material SET stok=%s, updated_at=%s WHERE id=%s", (new_stok, datetime.now(), id))
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('warehouse_inventory'))
    
    # GET request - fetch material data
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE id=%s", (id,))
            material = cursor.fetchone()
    finally:
        connection.close()
    
    if not material:
        return redirect(url_for('warehouse_inventory'))
    
    return render_template('warehouse/update_stock.html', material=material)

@app.route('/warehouse/download-report')
def download_warehouse_report():
    if not check_role_access('Warehouse Staff'):
        return redirect(url_for('login'))
    
    pdf_path = os.path.join(DOWNLOAD_FOLDER, f"warehouse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_report_pdf(pdf_path, 'Warehouse')
    return send_file(pdf_path, as_attachment=True, download_name="warehouse_report.pdf")

# ==================== PROCUREMENT STAFF ROUTES ====================

@app.route("/procurement/home")
def procurement_home():
    if not check_role_access('Procurement Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE status='Buy' ORDER BY level, part_code")
            buy_items = cursor.fetchall()
            cursor.execute("SELECT * FROM material WHERE stok < 5 AND status='Buy'")
            need_to_buy = cursor.fetchall()
            
    finally:
        connection.close()
    
    return render_template('procurement/home.html', 
                         buy_items=buy_items,
                         need_to_buy=need_to_buy,
                         total_buy_items=len(buy_items),
                         urgent_items_count=len(need_to_buy))

@app.route("/procurement/purchase-orders")
def procurement_purchase_orders():
    if not check_role_access('Procurement Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE status='Buy' ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('procurement/purchase_orders.html', material=data)

@app.route("/procurement/suppliers")
def procurement_suppliers():
    if not check_role_access('Procurement Staff'):
        return redirect(url_for('login'))
    
    return render_template('procurement/suppliers.html')

@app.route("/procurement/vendor-management")
def procurement_vendor_management():
    if not check_role_access('Procurement Staff'):
        return redirect(url_for('login'))
    
    return render_template('procurement/vendor_management.html')

@app.route('/procurement/download-report')
def download_procurement_report():
    if not check_role_access('Procurement Staff'):
        return redirect(url_for('login'))
    
    pdf_path = os.path.join(DOWNLOAD_FOLDER, f"procurement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_report_pdf(pdf_path, 'Procurement')
    return send_file(pdf_path, as_attachment=True, download_name="procurement_report.pdf")

# ==================== LEGACY ROUTES (For Backward Compatibility) ====================

@app.route("/about")
def about():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    return render_template('about.html')

@app.route("/stok")
def stok():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    # Redirect to role-specific stock page
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_stock'))
    elif role == 'Warehouse Staff':
        return redirect(url_for('warehouse_inventory'))
    else:
        return redirect(url_for('home'))

@app.route('/addMaterial', methods=['GET', 'POST'])
def add_material():
    # Redirect to role-specific add material page
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_add_material'))
    else:
        return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    # Redirect to role-specific edit material page
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_edit_material', id=id))
    else:
        return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_material(id):
    # Redirect to role-specific delete material
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_delete_material', id=id))
    else:
        return redirect(url_for('home'))

@app.route('/editstk/<int:id>', methods=['GET', 'POST'])
def edit_stok(id):
    # Redirect to role-specific edit stock
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('production_edit_stok', id=id))
    elif role == 'Warehouse Staff':
        return redirect(url_for('warehouse_update_stock', id=id))
    else:
        return redirect(url_for('home'))

@app.route('/download-report')
def download_report():
    # Redirect to role-specific download report
    role = session.get('role')
    if role == 'Production Staff':
        return redirect(url_for('download_production_report'))
    elif role == 'Finance Staff':
        return redirect(url_for('download_finance_report'))
    elif role == 'Warehouse Staff':
        return redirect(url_for('download_warehouse_report'))
    elif role == 'Procurement Staff':
        return redirect(url_for('download_procurement_report'))
    else:
        return redirect(url_for('home'))

# ==================== UTILITY FUNCTIONS ====================

def generate_report_pdf(file_path, department='General'):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if department == 'Procurement':
                cursor.execute("SELECT * FROM material WHERE status='Buy' ORDER BY level, part_code")
            else:
                cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()

    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center alignment
    title = Paragraph(f"{department} Bill Of Material Report", title_style)
    elements.append(title)
    
    # Date
    tanggal = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    info = Paragraph(f"<br/>Generated on: {tanggal}<br/>Department: {department}<br/><br/>", styles['Normal'])
    elements.append(info)

    # Table content
    table_data = [["Level", "Part Code", "Description", "Lot Size", "UOM", "Stock", "Status"]]
    for row in data:
        table_data.append([
            str(row[1]),  # level
            str(row[2]),  # part_code
            str(row[3]),  # deskripsi
            str(row[4]),  # lot_size
            str(row[5]),  # UOM
            str(row[6]),  # stok
            str(row[7])   # status
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table)
    doc.build(elements)

# Create download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)