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

@app.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('base.html', material=data)

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
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material ORDER BY level, part_code")
            data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('stok.html', material=data)

@app.route('/addMaterial', methods=['GET', 'POST'])
def add_material():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    if request.method == 'POST':
        level = request.form['level']
        part_code = request.form['part_code']
        deskripsi = request.form['deskripsi']
        lot_size = request.form['lot_size']
        UOM = request.form['UOM']
        status = request.form['status']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if part_code already exists
                cursor.execute("SELECT id FROM material WHERE part_code = %s", (part_code,))
                if cursor.fetchone():
                    return render_template('addMaterial.html', error='Part code already exists')
                
                cursor.execute(
                    "INSERT INTO material (level, part_code, deskripsi, lot_size, UOM, stok, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (level, part_code, deskripsi, lot_size, UOM, 0, status, datetime.now(), datetime.now())
                )
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('home'))
    
    return render_template('addMaterial.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_level = request.form['level']
        new_part_code = request.form['part_code']
        new_deskripsi = request.form['deskripsi']
        new_lot_size = request.form['lot_size']
        new_UOM = request.form['UOM']
        new_status = request.form['status']
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE material SET level=%s, part_code=%s, deskripsi=%s, lot_size=%s, UOM=%s, status=%s, updated_at=%s WHERE id=%s",
                    (new_level, new_part_code, new_deskripsi, new_lot_size, new_UOM, new_status, datetime.now(), id)
                )
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('home'))
    
    # GET request - fetch material data
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE id=%s", (id,))
            material = cursor.fetchone()
    finally:
        connection.close()
    
    if not material:
        return redirect(url_for('home'))
    
    return render_template('edit_material.html', material=material)

@app.route('/delete/<int:id>')
def delete_material(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM material WHERE id=%s", (id,))
            connection.commit()
    finally:
        connection.close()
    return redirect(url_for('home'))

@app.route('/editstk/<int:id>', methods=['GET', 'POST'])
def edit_stok(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_stok = request.form['stok']
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE material SET stok=%s, updated_at=%s WHERE id=%s", (new_stok, datetime.now(), id))
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('stok'))
    
    # GET request - fetch material data
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material WHERE id=%s", (id,))
            material = cursor.fetchone()
    finally:
        connection.close()
    
    if not material:
        return redirect(url_for('stok'))
    
    return render_template('edit_stok.html', material=material)

@app.route('/download-report')
def download_report():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'role' not in session:
        return redirect(url_for('role_selection'))
    
    pdf_path = os.path.join(DOWNLOAD_FOLDER, f"material_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_report_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name="material_report.pdf")

def generate_report_pdf(file_path):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
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
    title = Paragraph("Bill Of Material Report", title_style)
    elements.append(title)
    
    # Date
    tanggal = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    info = Paragraph(f"<br/>Generated on: {tanggal}<br/><br/>", styles['Normal'])
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