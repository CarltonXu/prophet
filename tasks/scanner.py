# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Scanner Celery tasks"""

import logging
from celery_app import celery
from services.scanner_service import ScannerService

logger = logging.getLogger(__name__)


@celery.task(bind=True, name='tasks.scan_network')
def scan_network_task(self, scan_task_id: int, host: str, nmap_args: str = None):
    """Celery task for network scanning"""
    try:
        logger.info(f"Starting scan task {scan_task_id} for {host}")
        service = ScannerService(scan_task_id)
        results = service.scan_and_save(host, nmap_args)
        logger.info(f"Scan task {scan_task_id} completed with {len(results)} hosts")
        return {'status': 'success', 'results_count': len(results)}
    except Exception as e:
        logger.error(f"Scan task {scan_task_id} failed: {e}")
        raise

