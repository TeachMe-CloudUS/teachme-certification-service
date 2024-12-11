# routes/health_routes.py
from flask import Blueprint, jsonify
from certification_service.health import HealthCheck
from certification_service.database import db_connection
from certification_service.config import CERTIFICATES_DIR

monitoring_bp = Blueprint('monitoring', __name__)

# Initialize health checker
health_checker = HealthCheck(
    service_name='certification-service',
    dependencies={
        'database': db_connection,
        'certificates_dir': CERTIFICATES_DIR
    }
)

# Health check endpoint to verify service and dependency health
@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that verifies service and dependency health."""
    return jsonify(*health_checker.get_health_status())