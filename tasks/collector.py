# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Collector Celery tasks"""

import logging
from celery_app import celery
from services.collector_service import CollectorService
from services.platform_collector_service import PlatformCollectorService

logger = logging.getLogger(__name__)


@celery.task(bind=True, name='tasks.collect_hosts')
def collect_hosts_task(self, collection_task_id: int, concurrent_limit: int = None):
    """Celery task for host collection"""
    try:
        logger.info(f"Starting collection task {collection_task_id}")
        service = CollectorService(collection_task_id)
        service.collect_hosts(concurrent_limit)
        logger.info(f"Collection task {collection_task_id} completed")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Collection task {collection_task_id} failed: {e}")
        raise


@celery.task(bind=True, name='tasks.collect_platform_hosts')
def collect_platform_hosts_task(self, collection_task_id: int, platform_id: int):
    """Celery task for platform host collection"""
    try:
        logger.info(f"Starting platform collection task {collection_task_id} for platform {platform_id}")
        service = PlatformCollectorService(collection_task_id, platform_id)
        service.collect_platform_hosts()
        logger.info(f"Platform collection task {collection_task_id} completed")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Platform collection task {collection_task_id} failed: {e}")
        raise

