import os
import logging
from datetime import datetime
from typing import Dict, Any
from logger import logger

class HealthCheck:
    def __init__(self, service_name: str, dependencies: Dict[str, Any]):
        """
        Initialize health checker with service name and dependencies.
        
        Args:
            service_name: Name of the service
            dependencies: Dictionary of dependency objects (e.g., database connection)
        """
        self.service_name = service_name
        self.dependencies = dependencies
        self.health_checks = {
            'database': self._check_database,
            'filesystem': self._check_filesystem
        }

    def get_health_status(self) -> tuple[Dict[str, Any], int]:
        """
        Get comprehensive health status of the service and its dependencies.
        
        Returns:
            Tuple of (health_status_dict, http_status_code)
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': self.service_name,
            'version': os.getenv('SERVICE_VERSION', '1.0.0'),
            'dependencies': {}
        }

        # Run all health checks
        for dep_name, check_func in self.health_checks.items():
            try:
                status, message = check_func()
                health_status['dependencies'][dep_name] = {
                    'status': status,
                    'message': message
                }
            except Exception as e:
                health_status['dependencies'][dep_name] = {
                    'status': 'unhealthy',
                    'message': str(e)
                }

        # Determine overall health
        is_healthy = all(
            dep['status'] == 'healthy'
            for dep in health_status['dependencies'].values()
        )

        if not is_healthy:
            health_status['status'] = 'unhealthy'
            return health_status, 500

        return health_status, 200

    def _check_database(self) -> tuple[str, str]:
        """Check database connection health."""
        db_connection = self.dependencies.get('database')
        if not db_connection:
            return 'unhealthy', 'Database connection not configured'

        is_healthy, message = db_connection.check_connection()
        return 'healthy' if is_healthy else 'unhealthy', message

    def _check_filesystem(self) -> tuple[str, str]:
        """Check filesystem health for certificates directory."""
        certificates_dir = self.dependencies.get('certificates_dir')
        if not certificates_dir:
            return 'unhealthy', 'Certificates directory not configured'

        if os.path.isdir(certificates_dir) and os.access(certificates_dir, os.W_OK):
            return 'healthy', 'certificates directory is accessible'
        return 'unhealthy', 'certificates directory is not accessible'
