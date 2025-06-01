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
    if 'username' in session:
        return f"Halo, {session['username']}! <a href='/logout'>Logout</a>"
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/home")
def home():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material")
            data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('base.html', material=data)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/stok")
def stok():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material")
            data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('stok.html', material=data)

@app.route('/addMaterial', methods=['GET', 'POST'])
def add_material():
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
                cursor.execute(
                    "INSERT INTO material (level, part_code, deskripsi, lot_size, UOM, stok, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (level, part_code, deskripsi, lot_size, UOM, 0, status)
                )
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('home'))
    return render_template('addMaterial.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
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
                    "UPDATE material SET level=%s, part_code=%s, deskripsi=%s, lot_size=%s, UOM=%s, status=%s WHERE id=%s",
                    (new_level, new_part_code, new_deskripsi, new_lot_size, new_UOM, new_status, id)
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
    
    return render_template('edit_material.html', material=material)

@app.route('/delete/<int:id>')
def delete_material(id):
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
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_stok = request.form['stok']
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE material SET stok=%s WHERE id=%s", (new_stok, id))
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
    
    return render_template('edit_stok.html', material=material)

@app.route('/download-report')
def download_report():
    pdf_path = os.path.join(DOWNLOAD_FOLDER, "report.pdf")
    generate_report_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True)

def generate_report_pdf(file_path):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM material")
            data = cursor.fetchall()
    finally:
        connection.close()

    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['h1']
    title_style.alignment = 1
    title = Paragraph("Laporan Data Material", title_style)
    elements.append(title)
    
    tanggal = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    info = Paragraph(f"Tanggal Pembuatan: {tanggal}", styles['Normal'])
    info.spaceAfter = 10
    elements.append(info)

    # Table content
    table_data = [["ID", "Level", "Part Code", "Deskripsi", "Lot Size", "UOM", "Stock", "Status"]]
    for row in data:
        table_data.append([str(x) for x in row])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0, 0), (-1, -1), 1)
    ]))
    elements.append(table)
    doc.build(elements)

# Create download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)