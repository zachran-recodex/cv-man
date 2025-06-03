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
        return redirect(url_for('production_mps'))
    elif role == 'Finance Staff':
        return redirect(url_for('finance_home'))
    elif role == 'Warehouse Staff':
        return redirect(url_for('warehouse_home'))
    elif role == 'Procurement Staff':
        return redirect(url_for('procurement_home'))
    else:
        return redirect(url_for('role_selection'))

# ==================== PRODUCTION MPS ROUTES ====================

@app.route("/production/mps")
def production_mps():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM mps ORDER BY schedule DESC")
            mps_data = cursor.fetchall()
            
            # Calculate statistics
            cursor.execute("SELECT COUNT(*) FROM mps WHERE status = 'Planned'")
            planned_orders_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mps WHERE status = 'In Progress'")
            in_progress_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mps WHERE status = 'Completed'")
            completed_count = cursor.fetchone()[0]
            
    finally:
        connection.close()
    
    return render_template('production/mps/index.html', 
                         mps_data=mps_data,
                         planned_orders_count=planned_orders_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count)

@app.route("/production/mps/add", methods=['GET', 'POST'])
def production_add_mps():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        product = request.form['product']
        product_quantity = request.form['product_quantity']
        schedule = request.form['schedule']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO mps (product, product_quantity, schedule, status, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (product, product_quantity, schedule, 'Planned', datetime.now())
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_mps'))
    
    return render_template('production/mps/create.html')

@app.route("/production/mps/edit/<int:id>", methods=['GET', 'POST'])
def production_edit_mps(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        product = request.form['product']
        product_quantity = request.form['product_quantity']
        schedule = request.form['schedule']
        status = request.form['status']
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE mps SET product=%s, product_quantity=%s, schedule=%s, status=%s, updated_at=%s WHERE id=%s",
                    (product, product_quantity, schedule, status, datetime.now(), id)
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_mps'))
    
    # GET request
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM mps WHERE id=%s", (id,))
            mps = cursor.fetchone()
    finally:
        connection.close()
    
    if not mps:
        return redirect(url_for('production_mps'))
    
    return render_template('production/mps/update.html', mps=mps)

@app.route("/production/mps/delete/<int:id>")
def production_delete_mps(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM mps WHERE id=%s", (id,))
            connection.commit()
    finally:
        connection.close()
    
    return redirect(url_for('production_mps'))

# ==================== PRODUCTION MATERIAL AVAILABILITY ROUTES ====================

@app.route("/production/material")
def production_material():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY material_code")
            materials = cursor.fetchall()
            
            # Calculate statistics
            total_materials = len(materials)
            available_count = len([m for m in materials if m[6] == 'available'])
            in_delivery_count = len([m for m in materials if m[6] == 'in deliveries'])
            rejected_count = len([m for m in materials if m[6] == 'rejected'])
            
    finally:
        connection.close()
    
    return render_template('production/material_availibility/index.html', 
                         materials=materials,
                         total_materials=total_materials,
                         available_count=available_count,
                         in_delivery_count=in_delivery_count,
                         rejected_count=rejected_count)

@app.route("/production/material/add", methods=['GET', 'POST'])
def production_add_material():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        material = request.form['material']
        material_code = request.form['material_code']
        description = request.form['description']
        lot_size = request.form['lot_size']
        uom = request.form['uom']
        status = request.form['status']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO material (material, material_code, description, lot_size, uom, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (material, material_code, description, lot_size, uom, status, datetime.now())
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_material'))
    
    return render_template('production/material_availibility/create.html')

@app.route("/production/material/edit/<int:id>", methods=['GET', 'POST'])
def production_edit_material(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        material = request.form['material']
        material_code = request.form['material_code']
        description = request.form['description']
        lot_size = request.form['lot_size']
        uom = request.form['uom']
        status = request.form['status']
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE material SET material=%s, material_code=%s, description=%s, lot_size=%s, uom=%s, status=%s, updated_at=%s WHERE id=%s",
                    (material, material_code, description, lot_size, uom, status, datetime.now(), id)
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_material'))
    
    # GET request
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE id=%s", (id,))
            material = cursor.fetchone()
    finally:
        connection.close()
    
    if not material:
        return redirect(url_for('production_material'))
    
    return render_template('production/material_availibility/update.html', material=material)

@app.route("/production/material/delete/<int:id>")
def production_delete_material(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM material WHERE id=%s", (id,))
            connection.commit()
    finally:
        connection.close()
    
    return redirect(url_for('production_material'))

# ==================== PRODUCTION PROCUREMENT ROUTES ====================

@app.route("/production/procurement")
def production_procurement():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM procurement ORDER BY date_needed ASC")
            procurements = cursor.fetchall()
            
            # Calculate statistics and add urgency flag to each procurement
            total_requests = len(procurements)
            today = datetime.now().date()
            urgent_requests = 0
            
            # Add urgency information to each procurement record
            enhanced_procurements = []
            for procurement in procurements:
                # procurement[3] is date_needed
                is_urgent = procurement[3] <= today
                if is_urgent:
                    urgent_requests += 1
                
                # Add the urgency flag to the procurement data
                enhanced_procurement = list(procurement) + [is_urgent]
                enhanced_procurements.append(enhanced_procurement)
            
    finally:
        connection.close()
    
    return render_template('production/procurement/index.html', 
                        procurements=enhanced_procurements,
                        total_requests=total_requests,
                        urgent_requests=urgent_requests)

@app.route("/production/procurement/add", methods=['GET', 'POST'])
def production_add_procurement():
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        request_goods = request.form['request_goods']
        date_request = request.form['date_request']
        date_needed = request.form['date_needed']
        quantity = request.form['quantity']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO procurement (request_goods, date_request, date_needed, quantity, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (request_goods, date_request, date_needed, quantity, datetime.now())
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_procurement'))
    
    return render_template('production/procurement/create.html')

@app.route("/production/procurement/edit/<int:id>", methods=['GET', 'POST'])
def production_edit_procurement(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        request_goods = request.form['request_goods']
        date_request = request.form['date_request']
        date_needed = request.form['date_needed']
        quantity = request.form['quantity']
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE procurement SET request_goods=%s, date_request=%s, date_needed=%s, quantity=%s, updated_at=%s WHERE id=%s",
                    (request_goods, date_request, date_needed, quantity, datetime.now(), id)
                )
                connection.commit()
        finally:
            connection.close()
        
        return redirect(url_for('production_procurement'))
    
    # GET request
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM procurement WHERE id=%s", (id,))
            procurement = cursor.fetchone()
    finally:
        connection.close()
    
    if not procurement:
        return redirect(url_for('production_procurement'))
    
    return render_template('production/procurement/update.html', procurement=procurement)

@app.route("/production/procurement/delete/<int:id>")
def production_delete_procurement(id):
    if not check_role_access('Production Staff'):
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM procurement WHERE id=%s", (id,))
            connection.commit()
    finally:
        connection.close()
    
    return redirect(url_for('production_procurement'))

if __name__ == '__main__':
    app.run(debug=True)