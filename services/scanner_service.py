# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Scanner service to wrap NetworkController"""

import logging
from typing import List, Dict
from prophet.scanner.network import NetworkController
from models import Host, ScanTask, db
from datetime import datetime

logger = logging.getLogger(__name__)


class ScannerService:
    """Service for network scanning"""
    
    def __init__(self, scan_task_id: int):
        """Initialize scanner service with task ID"""
        self.scan_task_id = scan_task_id
        self.scan_task = ScanTask.query.get(scan_task_id)
        if not self.scan_task:
            raise ValueError(f"Scan task {scan_task_id} not found")
    
    def update_progress(self, progress: int, current_host: str = None, result_count: int = None):
        """Update scan task progress"""
        self.scan_task.progress = progress
        if current_host:
            self.scan_task.current_host = current_host
        if result_count is not None:
            self.scan_task.result_count = result_count
        db.session.commit()
    
    def scan_and_save(self, host: str, nmap_args: str = None) -> List[Dict]:
        """Scan network and save results to database"""
        try:
            # Update status to running
            self.scan_task.status = 'running'
            self.scan_task.started_at = datetime.utcnow()
            db.session.commit()
            
            # Initialize scanner
            # Use a temporary output path (we'll handle results in memory)
            import tempfile
            import os
            temp_dir = tempfile.mkdtemp()
            
            try:
                scanner = NetworkController(host, nmap_args, temp_dir)
                scanner.generate_report()
                
                # Read results from CSV
                import pandas as pd
                csv_path = os.path.join(temp_dir, 'scan_hosts.csv')
                
                if not os.path.exists(csv_path):
                    logger.warning(f"Scan results file not found: {csv_path}")
                    return []
                
                df = pd.read_csv(csv_path, keep_default_na=False)
                
                # Update progress
                total_hosts = len(df)
                saved_hosts = []
                errors = []  # Track errors for reporting
                
                for idx, row in df.iterrows():
                    host_ip = row.get('ip', 'unknown')
                    try:
                        # Check if host already exists
                        existing_host = Host.query.filter_by(ip=host_ip, deleted_at=None).first()
                        
                        if existing_host:
                            # Update existing host
                            self._update_host_from_scan(existing_host, row)
                            host_obj = existing_host
                        else:
                            # Create new host
                            host_obj = self._create_host_from_scan(row)
                            db.session.add(host_obj)
                        
                        db.session.flush()
                        saved_hosts.append(host_obj)
                        
                        # Update progress
                        progress = int((idx + 1) / total_hosts * 100)
                        self.update_progress(progress, current_host=host_ip, result_count=len(saved_hosts))
                        
                    except Exception as e:
                        # Handle IntegrityError (UNIQUE constraint failed)
                        from sqlalchemy.exc import IntegrityError
                        if isinstance(e, IntegrityError) and 'UNIQUE constraint failed: hosts.ip' in str(e):
                            # Rollback the failed transaction
                            db.session.rollback()
                            # Try to find and update existing host
                            try:
                                existing_host = Host.query.filter_by(ip=host_ip, deleted_at=None).first()
                                if existing_host:
                                    self._update_host_from_scan(existing_host, row)
                                    db.session.commit()
                                    saved_hosts.append(existing_host)
                                    logger.info(f"Updated existing host {host_ip} after UNIQUE constraint error")
                                else:
                                    errors.append(f"Host {host_ip}: UNIQUE constraint failed but host not found")
                            except Exception as e2:
                                errors.append(f"Host {host_ip}: Error updating after UNIQUE constraint: {e2}")
                                db.session.rollback()
                        else:
                            # Other errors
                            db.session.rollback()
                            errors.append(f"Host {host_ip}: {str(e)}")
                            logger.error(f"Error saving host {host_ip}: {e}")
                        continue
                
                # Commit all changes
                db.session.commit()
                
                # Log error summary
                if errors:
                    error_summary = f"Scan task {self.scan_task_id} completed with {len(errors)} errors: {', '.join(errors[:10])}"
                    if len(errors) > 10:
                        error_summary += f" ... and {len(errors) - 10} more"
                    logger.warning(error_summary)
                
                # Update task status
                self.scan_task.status = 'completed'
                self.scan_task.completed_at = datetime.utcnow()
                self.scan_task.result_count = len(saved_hosts)
                self.scan_task.progress = 100
                db.session.commit()
                
                return [h.to_dict() for h in saved_hosts]
                
            finally:
                # Cleanup temp directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"Scan task {self.scan_task_id} failed: {e}")
            self.scan_task.status = 'failed'
            self.scan_task.error_message = str(e)
            self.scan_task.completed_at = datetime.utcnow()
            db.session.commit()
            raise
    
    def _create_host_from_scan(self, row: Dict) -> Host:
        """Create Host object from scan result row"""
        return Host(
            hostname=row.get('hostname', '') or None,
            ip=row.get('ip', ''),
            mac=row.get('mac', '') or None,
            vendor=row.get('vendor', '') or None,
            os_type=row.get('os', '') or None,
            os_version=row.get('version', '') or None,
            device_type='host' if row.get('os') else 'network_device',
            is_physical=True,  # Default to physical, will be updated during collection
            source='scan',
            source_scan_task_id=self.scan_task_id,
            created_by=self.scan_task.created_by,
        )
    
    def _update_host_from_scan(self, host: Host, row: Dict):
        """Update existing Host from scan result"""
        if not host.hostname and row.get('hostname'):
            host.hostname = row['hostname']
        if not host.mac and row.get('mac'):
            host.mac = row['mac']
        if not host.vendor and row.get('vendor'):
            host.vendor = row['vendor']
        if not host.os_type and row.get('os'):
            host.os_type = row['os']
        if not host.os_version and row.get('version'):
            host.os_version = row['version']
        # Update source if not set
        if not host.source:
            host.source = 'scan'
            host.source_scan_task_id = self.scan_task_id

