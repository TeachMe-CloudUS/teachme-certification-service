import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pyhanko import stamp
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils import text
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata
from certification_service.logger import logger
from certification_service.database import db_connection
from certification_service.blob_storage import blob_storage_service
from certification_service.kafka.producer import send_certification_notification
from certification_service.models.student_course_data import Student_Course_Data
import certification_service.config as config
from datetime import datetime

def generate_certificate(student_course_data):
    """Generate and sign a PDF certificate for a student and a specific course."""
    logger.info("Starting creating certificate...")
    # Create a PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Add certificate content
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "Certificate of Completion")
    c.setFont("Helvetica", 16)
    c.drawCentredString(
        width / 2,
        height - 250,
        f"{student_course_data.student_name} "
        f"{student_course_data.student_surname} "
        f"successfully completed the {student_course_data.course_level} "
        f"course {student_course_data.course_name} "
        f"with full academic requirements on {student_course_data.completionDate}."
    )
    c.save()

    # Rest of the function remains the same...

    # Prepare the PDF for signing
    pdf_buffer.seek(0)
    pdf_writer = IncrementalPdfFileWriter(pdf_buffer)

    # Create and append the signature field
    sig_field_spec = SigFieldSpec(
        sig_field_name=config.SIGNATURE_FIELD_NAME,
        box=config.SIGNATURE_BOX
    )
    append_signature_field(pdf_writer, sig_field_spec=sig_field_spec)

    # Load the signer
    pfx_path = os.path.join(config.CERTIFICATES_DIR, "certificate.pfx")
    logger.info("Attempting to create signer from PFX file...")
    signer = signers.SimpleSigner.load_pkcs12(pfx_path, passphrase=config.PFX_PASSPHRASE.encode())
    

    # Define the QR stamp style
    qr_stamp_style = stamp.QRStampStyle(
        stamp_text='Signed by: %(signer)s\nTime: %(ts)s\nURL: %(url)s',
        text_box_style=text.TextBoxStyle()
    )

    # Sign the PDF
    meta = PdfSignatureMetadata(field_name=config.SIGNATURE_FIELD_NAME)
    pdf_signer = signers.PdfSigner(meta, signer=signer, stamp_style=qr_stamp_style)
    logger.info("Attempting to sign PDF with QR code...")
    signed_pdf_stream = pdf_signer.sign_pdf(
        pdf_writer, appearance_text_params={'url': config.QR_CODE_URL}
    )
    logger.info("PDF signed with QR code successfully.")
    return signed_pdf_stream

def certify_student(student_course_data: Student_Course_Data = None):
    """Generate and sign a PDF certificate for a student and a specific course."""
    # Generate the certificate
    cert_stream = generate_certificate(student_course_data)

    # Generate unique blob name for the certificate
    blob_name = f"stud_{student_course_data.student_id}_course_{student_course_data.course_id}.pdf"

    # Upload the signed PDF to Azure Blob Storage
    blob_url = blob_storage_service.upload_file_from_stream(cert_stream, blob_name)
    logger.info(f"Signed PDF uploaded to: {blob_url}")

    # Store the certificate in the database
    stored_cert = db_connection.store_certificate(student_course_data, blob_url)
    
    if not stored_cert:
        logger.error(f"Failed to store certificate for student {student_course_data.student_id} " 
        f"in course {student_course_data.course_id}")
        blob_storage_service.delete_blob(blob_name)
        
        return None

    # Send success notification
    send_certification_notification(student_course_data, blob_url, True)

    return blob_url

def update_certs(student_id):
    """Update certificates for a student and return list of updated certificates."""
    # Implement the logic to update certificates
    dummy_path_list = [os.path.join(config.CERTIFICATES_DIR, f"dummy_certificate_{student_id}.pdf")]
    return dummy_path_list

def get_all_certs(student_id):
    """Get all certificates for a student."""
    # Implement the logic to get all certificates
    course_list = db_connection.get_all_course_certs(student_id)
    return course_list

def get_cert(student_id, course_id):
    """Get certificate for a specific course and student."""
    # Implement the logic to get a specific certificate
    cert_link = db_connection.get_course_cert(student_id, course_id)
    return cert_link

def delete_all_certs(student_id):
    """Delete all certificates for a student."""
    # Implement the logic to delete certificates
    # Delete first all certificates form blob and then links from db
    deleted_cert_count = db_connection.delete_all_certs(student_id)
    return deleted_cert_count
