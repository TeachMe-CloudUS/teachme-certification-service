import io
import os
import config
from logger import logger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pyhanko import stamp
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils import text
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata


def generate_certificate(student_data):
    """Generate and sign a PDF certificate for a student."""
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
        f"has successfully completed the course {student_data['course']}"
    )
    c.save()

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
