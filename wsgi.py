"""
WSGI entry point for gunicorn
This ensures the app can be properly imported
"""
import os
import sys
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("="*70)
logger.info("Starting WSGI application...")
logger.info("="*70)

try:
    logger.info("Importing backend_rag_api...")
    from backend_rag_api import app
    logger.info("✓ Successfully imported backend_rag_api.app")
    logger.info(f"✓ App type: {type(app)}")
    logger.info("="*70)
except Exception as e:
    logger.error(f"✗ Failed to import app: {e}", exc_info=True)
    raise

# This is what gunicorn will use
application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port)

