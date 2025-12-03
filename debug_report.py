import sys
import logging
from automated_insight_engine.main import main

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('report_generation.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("Starting report generation with debug logging...")
    main()
    logger.info("Report generation completed successfully")
except Exception as e:
    logger.error(f"Error generating reports: {str(e)}", exc_info=True)
    raise
