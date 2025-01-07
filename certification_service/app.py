# app.py
"""
This module provides a certification service using Flask.
"""
from asn1crypto.ocsp import Certificates
from flask import Flask
from dotenv import load_dotenv
from certification_service.logger import logger
import threading
from certification_service.routes.certification_routes import certification_bp
from certification_service.routes.monitoring_routes import monitoring_bp
from certification_service.cert_management import ensure_certificate_and_key_exist
from certification_service.database import db_connection
from certification_service.kafka.consumer import start_consumer
from certification_service.routes.certification_routes import certification_bp
from flasgger import Swagger

# Register the Blueprint
def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    swagger_config = {
        "headers": [
        ],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/swagger/certification-service/api-docs',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    swagger = Swagger(app, config=swagger_config, template={
        "info": {
            "title": "Teachme Certification Service API",
            "description": "TeachMe Certification Service is a microservice responsible for generating, managing, and validating certificates for students completing courses on the TeachMe platform. This service creates digitally signed PDF certificates, ensuring their authenticity and accessibility for successful learners. The service is built with Flask and can be containerized using Docker for seamless deployment and scalability in cloud environments.",
            "version": "1.0.0",
            "tags": [
                {
                    "name": "Certificate Operations",
                    "description": "API for managing certificates"
                }
            ]
        }
    })
    app.register_blueprint(certification_bp)

    # Start Kafka consumer
    def run_consumer():
        try:
            logger.info("Starting Kafka consumer...")
            start_consumer()
            logger.info("Kafka consumer started successfully")

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {str(e)}")

    # Initialize database connection
    try:
        db_connection.init_mongodb()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

    consumer_thread = threading.Thread(target=run_consumer)
    consumer_thread.start()

    # Call the function to ensure the certificate, key, and PFX file exist
    ensure_certificate_and_key_exist()

    app.register_blueprint(monitoring_bp)

    return app

# Load environment variables from .env file 
load_dotenv()

# Global app instance
app = create_app()

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
