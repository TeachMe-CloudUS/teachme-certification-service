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
from certification_service.database import db_connection, get_mock_student_data, get_mock_course_data
import certification_service.config as config



#Define the signature field name and box
def generate_certificate(student_id,course_id):
    """Generate and sign a PDF certificate for a student and a specific course."""
    # Get mock student data
    student_data = get_mock_student_data(student_id)

    #Get mock course data
    course_data = get_mock_course_data(course_id)

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
    c.drawCentredString(
         width / 2,
        height - 250,
        f"has successfully completed the course '{course_data['name']}' "
        f"in {course_data['duration']} "
        f"on {student_data['graduation_date']}."
    )

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
    logger.info("Signer created successfully.")

    # Define the QR stamp style
    qr_stamp_style = stamp.QRStampStyle(
        stamp_text='Signed by: %(signer)s\nTime: %(ts)s\nURL: %(url)s',
        text_box_style=text.TextBoxStyle()
    )

    # Sign the PDF
    meta = PdfSignatureMetadata(field_name=config.SIGNATURE_FIELD_NAME)
    pdf_signer = signers.PdfSigner(meta, signer=signer, stamp_style=qr_stamp_style)
    logger.info("Attempting to sign PDF with QR code...")
    signed_pdf = pdf_signer.sign_pdf(
        pdf_writer, appearance_text_params={'url': config.QR_CODE_URL}
    )
    logger.info("PDF signed with QR code successfully.")

    # Save the signed PDF
    filename = os.path.join(config.CERTIFICATES_DIR, f"course_{student_data['course']}stud_{student_data['id']}.pdf")
    with open(filename, "wb") as f:
        f.write(signed_pdf.getvalue())
    logger.info("Signed PDF saved successfully.")

    return filename

def certify_student(student_id, course_id):
    """Generate and sign a PDF certificate for a student and a specific course."""
    certificate_path = generate_certificate(student_id, course_id)
    return certificate_path

def update_certs(student_id):
    """Update certificates for a student and return list of updated certificates."""
    # Implement the logic to update certificates
    dummy_path_list = [os.path.join(config.CERTIFICATES_DIR, f"dummy_certificate_{student_id}.pdf")]
    return dummy_path_list

def get_all_certs(student_id):
    """Get all certificates for a student."""
    # Implement the logic to get all certificates
    course_list = [69]
    return course_list

def get_cert(student_id, course_id):
    """Get certificate for a specific course and student."""
    # Implement the logic to get a specific certificate
    cert_link = db_connection.get_course_cert(student_id, course_id)
    return cert_link

def delete_all_certs(student_id):
    """Delete all certificates for a student."""
    # Implement the logic to delete certificates
    #Delete first all certificates form blob and then links from db
    deleted_cert_count = db_connection.delete_all_certs(student_id)
    return deleted_cert_count


