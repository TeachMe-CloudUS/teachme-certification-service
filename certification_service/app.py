# app.py
"""
This module provides a certification service using Flask.
"""
from flask import Flask
from dotenv import load_dotenv
from certification_service.logger import logger
from certification_service.routes.certification_routes import certification_bp
from certification_service.routes.monitoring_routes import monitoring_bp
from certification_service.cert_management import ensure_certificate_and_key_exist
from certification_service.database import db_connection
from certification_service.kafka.consumer import start_consumer

# Register the Blueprint
def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    # Initialize database connection
    try:
        db_connection.init_mongodb()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Initialize kafka
    try:
        start_consumer() 
        logger.info("Kafka consumer started") 
    except Exception as e:
        logger.error(f"Failed to initialize kafkaconsumer: {str(e)}")
        raise


    # Call the function to ensure the certificate, key, and PFX file exist
    ensure_certificate_and_key_exist()

    app.register_blueprint(certification_bp)
    app.register_blueprint(monitoring_bp)


    return app

# Load environment variab        
