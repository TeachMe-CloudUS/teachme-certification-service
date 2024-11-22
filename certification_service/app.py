# app.py
import os
import logging
from flask import Flask, jsonify, request
from pyhanko import stamp
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils import text
from dotenv import load_dotenv
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import json

# Load environment variables from .env file
load_dotenv()

# Configuration
CERTIFICATES_DIR = os.getenv('CERTIFICATES_DIR')
PFX_PASSPHRASE = os.getenv('PFX_PASSPHRASE')
SIGNATURE_FIELD_NAME = os.getenv('SIGNATURE_FIELD_NAME')
SIGNATURE_BOX = tuple(map(int, os.getenv('SIGNATURE_BOX').split(',')))
QR_CODE_URL = os.getenv('QR_CODE_URL')

# Ensure certificates directory exists
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("certification_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Function to ensure the private key, certificate, and PFX file exist
def ensure_certificate_and_key_exist():
    key_path = os.path.join(CERTIFICATES_DIR, "private.key")
    cert_path = os.path.join(CERTIFICATES_DIR, "certificate.crt")
    pfx_path = os.path.join(CERTIFICATES_DIR, "certificate.pfx")

    if not os.path.exists(key_path):
        logger.info("Private key not found. Generating a new private key...")
        subprocess.run([
            "openssl", "genpkey", "-algorithm", "RSA", "-out", key_path
        ])

    if not os.path.exists(cert_path):
        logger.info("Certificate not found. Generating a new self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-x509", "-nodes", "-days", "365",
            "-newkey", "rsa:2048", "-keyout", key_path, "-out", cert_path,
            "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=localhost"
        ])

    if not os.path.exists(pfx_path):
        logger.info("PFX file not found. Creating a new PFX file...")
        subprocess.run([
            "openssl", "pkcs12", "-export", "-out", pfx_path,
            "-inkey", key_path, "-in", cert_path,
            "-passout", f"pass:{PFX_PASSPHRASE}"
        ])

# Call the function to ensure the certificate, key, and PFX file exist
ensure_certificate_and_key_exist()

# Function to generate and sign a PDF certificate
def generate_certificate(student_data):
    # Create a PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Add certificate content
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "Certificate of Completion")
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2, height - 200, f"This certifies that {student_data['name']}")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 250, f"has successfully completed the course {student_data['course']}")
    c.save()

    # Prepare the PDF for signing
    pdf_buffer.seek(0)
    pdf_writer = IncrementalPdfFileWriter(pdf_buffer)

    # Create and append the signature field
    sig_field_spec = SigFieldSpec(
        sig_field_name=SIGNATURE_FIELD_NAME,
        box=SIGNATURE_BOX
    )
    append_signature_field(pdf_writer, sig_field_spec=sig_field_spec)

    # Load the signer
    pfx_path = os.path.join(CERTIFICATES_DIR, "certificate.pfx")
    logger.info("Attempting to create signer from PFX file...")
    signer = signers.SimpleSigner.load_pkcs12(pfx_path, passphrase=PFX_PASSPHRASE.encode())
    logger.info("Signer created successfully.")

    # Define the QR stamp style
    qr_stamp_style = stamp.QRStampStyle(
        stamp_text='Signed by: %(signer)s\nTime: %(ts)s\nURL: %(url)s',
        text_box_style=text.TextBoxStyle()
    )

    # Sign the PDF
    meta = signers.PdfSignatureMetadata(field_name=SIGNATURE_FIELD_NAME)
    pdf_signer = signers.PdfSigner(meta, signer=signer, stamp_style=qr_stamp_style)
    logger.info("Attempting to sign PDF with QR code...")
    signed_pdf = pdf_signer.sign_pdf(
        pdf_writer, appearance_text_params={'url': QR_CODE_URL}
    )
    logger.info("PDF signed with QR code successfully.")

    # Save the signed PDF
    filename = os.path.join(CERTIFICATES_DIR, f"certificate_{student_data['id']}.pdf")
    with open(filename, "wb") as f:
        f.write(signed_pdf.getvalue())
    logger.info("Signed PDF saved successfully.")

    return filename

# Function to get mock student data
def get_mock_student_data(student_id):
    return {
        'id': student_id,
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'course': 'Data Science',
        'graduation_date': '2023-06-30'
    }

# Route to certify a student
@app.route('/certify/<int:student_id>', methods=['POST'])
def certify_student(student_id):
    try:
        # Use mock student data
        student_data = get_mock_student_data(student_id)
        
        # Generate Certificate
        certificate_path = generate_certificate(student_data)
        
        # Log the event instead of publishing
        event_data = {
            'student_id': student_id,
            'name': student_data['name'],
            'certificate_path': certificate_path,
            'status': 'COMPLETED'
        }
        logger.info(f"Event: {json.dumps(event_data)}")
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate_path': certificate_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
