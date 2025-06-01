from flask import Flask, render_template, request, session, redirect, url_for, send_file
from flask_session import Session
from flask_mysqldb import MySQL
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import MySQLdb
import os

app = Flask(__name__, template_folder='template')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fri036_cvacy'
mysql = MySQL(app)

# Konfigurasi Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'
Session(app)

# Inisialisasi koneksi
mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'])

@app.route('/')
def index():
    # Cek apakah session 'username' tersedia
    if 'username' in session:
        return f"Halo, {session['username']}! <a href='/logout'>Logout</a>"
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Form login, menyimpan username ke session
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username  # Simpan session
        session['password'] = password  # Simpan session
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Logout dan hapus session
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/home")
def home():
    #  Menampilkan daftar data dari database
    cur = mysql.cursor()
    cur.execute("SELECT * FROM material")
    data = cur.fetchall()
    cur.close()
    return render_template('base.html', material=data)

@app.route("/about")
def about():
    # halamaan about isi sendiri ya, tentang produk ekspreso machinenya, kalau ga ngerti tanya
    if 'about' in session :
        return "<h1>Hello, ini halaman about!</h1>"
    return render_template('about.html')

@app.route("/stok")
def stok():
    #  Menampilkan daftar data dari database
    cur = mysql.cursor()
    cur.execute("SELECT * FROM material")
    data = cur.fetchall()
    cur.close()
    return render_template('stok.html', material=data)

#CRUD
@app.route('/addMaterial', methods=['GET', 'POST'])
def add_material():
    # Form untuk menambahkan data ke database
    if request.method == 'POST':
        level = request.form['Level']
        part_code = request.form['Part_Code']
        deskripsi = request.form['Deskripsi']
        lot_size = request.form['Lot_Size']
        UOM = request.form['UOM']
        status = request.form['Status']
        cur = mysql.cursor()
        cur.execute("INSERT INTO material (Level, Part_Code, Deskripsi, Lot_Size, UOM, Status) VALUES (%s, %s, %s, %s, %s, %s)", (level, part_code, deskripsi, lot_size, UOM, status))
        mysql.commit()
        cur.close()
        return redirect(url_for('home'))
    return render_template('addMaterial.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    #Form untuk mengedit data di database
    cur = mysql.cursor()
    cur.execute("SELECT * FROM material WHERE id=%s", (id,))
    material = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        new_level = request.form['Level']
        new_part_code = request.form['Part_Code']
        new_deskripsi = request.form['Deskripsi']
        new_lot_size = request.form['Lot_Size']
        new_UOM = request.form['UOM']
        new_status = request.form['Status']
        cur = mysql.cursor()
        cur.execute("UPDATE material SET Level=%s, Part_Code=%s, Deskripsi=%s, Lot_Size=%s, UOM=%s, Status=%s WHERE id=%s", (new_level, new_part_code,new_deskripsi, new_lot_size, new_UOM, new_status, id))
        mysql.commit()
        cur.close()
        return redirect(url_for('home'))

    return render_template('edit_material.html', material=material)

@app.route('/delete/<int:id>')
def delete_material(id):
    # Menghapus data dari database
    cur = mysql.cursor()
    cur.execute("DELETE FROM material WHERE id=%s", (id,))
    mysql.commit()
    cur.close()
    return redirect(url_for('home'))

@app.route('/editstk/<int:id>', methods=['GET', 'POST'])
def edit_stok(id):
    #Form untuk mengedit data di database
    cur = mysql.cursor()
    cur.execute("SELECT * FROM material WHERE id=%s", (id,))
    material = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        new_stok = request.form['stok']
        cur = mysql.cursor()
        cur.execute("UPDATE material SET stok=%s WHERE id=%s", (new_stok, id))
        mysql.commit()
        cur.close()
        return redirect(url_for('stok'))

    return render_template('edit_stok.html', material=material)

@app.route('/download-report')
def download_report():
    #Generate download PDF dari data MySQL
    pdf_path = os.path.join(DOWNLOAD_FOLDER, "report.pdf")
    generate_report_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True)

def generate_report_pdf(file_path):
    # Functions untuk collect data dari database dan generate PDF
    cur = mysql.cursor()
    cur.execute("SELECT * FROM material")
    data = cur.fetchall()
    cur.close()

    # Membuat PDF
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

    # Isi konten PDF Reporting
    table_data = [["id", "Level", "Part Code", "Deskripsi", "Lot Size", "UOM", "Status"]]
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

# Folder untuk menyimpan konten PDF
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.run(debug=True)