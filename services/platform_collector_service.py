# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Service for collecting platform hosts (VMware VMs, etc.)"""

import logging
from typing import List, Dict
from datetime import datetime
import tempfile
import shutil

from models import Host, HostDetail, VirtualizationPlatform, CollectionTask, db
from services.collection_parser_service import CollectionParserService

logger = logging.getLogger(__name__)


class PlatformCollectorService:
    """Service for collecting platform hosts"""
    
    def __init__(self, collection_task_id: int, platform_id: int):
        """Initialize platform collector service"""
        self.collection_task_id = collection_task_id
        self.collection_task = CollectionTask.query.get(collection_task_id)
        if not self.collection_task:
            raise ValueError(f"Collection task {collection_task_id} not found")
        
        self.platform_id = platform_id
        # Query platform with explicit column selection to ensure password_encrypted is loaded
        self.platform = VirtualizationPlatform.query.filter_by(
            id=platform_id,
            deleted_at=None
        ).first()
        if not self.platform:
            raise ValueError(f"Platform {platform_id} not found or deleted")
        
        # Log platform info for debugging
        logger.info(f"Initialized PlatformCollectorService for platform {self.platform.name} (ID: {platform_id})")
        logger.debug(f"Platform password_encrypted loaded: {self.platform.password_encrypted is not None}")
    
    def update_progress(self, completed: int = None, failed: int = None):
        """Update collection task progress"""
        if completed is not None:
            self.collection_task.completed_count = completed
        if failed is not None:
            self.collection_task.failed_count = failed
        
        # Calculate progress based on actual task hosts
        host_ids = self.collection_task.get_host_ids()
        total = len(host_ids)
        if total > 0:
            done = self.collection_task.completed_count + self.collection_task.failed_count
            self.collection_task.progress = int(done / total * 100)
        else:
            self.collection_task.progress = 0
        
        db.session.commit()
    
    def collect_platform_hosts(self):
        """Collect hosts from platform"""
        try:
            # Update status to running
            self.collection_task.status = 'running'
            self.collection_task.started_at = datetime.utcnow()
            db.session.commit()
            
            # Get host IDs to collect
            host_ids = self.collection_task.get_host_ids()
            if not host_ids:
                logger.warning(f"No hosts to collect for task {self.collection_task_id}")
                self.collection_task.status = 'completed'
                self.collection_task.completed_at = datetime.utcnow()
                db.session.commit()
                return
            
            # Get hosts
            hosts = Host.query.filter(
                Host.id.in_(host_ids),
                Host.deleted_at == None
            ).all()
            
            if not hosts:
                logger.warning(f"No valid hosts found for task {self.collection_task_id}")
                self.collection_task.status = 'completed'
                self.collection_task.completed_at = datetime.utcnow()
                db.session.commit()
                return
            
            # Collect based on platform type
            if self.platform.type == 'vmware':
                self._collect_vmware_hosts(hosts)
            else:
                logger.error(f"Platform type {self.platform.type} not supported for collection")
                self.collection_task.status = 'failed'
                self.collection_task.error_message = f"Platform type {self.platform.type} not supported"
                self.collection_task.completed_at = datetime.utcnow()
                db.session.commit()
                return
            
            # Update task status
            total = len(hosts)
            completed = self.collection_task.completed_count
            failed = self.collection_task.failed_count
            
            if failed == total:
                self.collection_task.status = 'failed'
            elif completed + failed == total:
                self.collection_task.status = 'completed'
            
            self.collection_task.completed_at = datetime.utcnow()
            self.collection_task.progress = 100
            db.session.commit()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Platform collection task {self.collection_task_id} failed: {e}")
            import traceback
            traceback_str = traceback.format_exc()
            logger.error(traceback_str)
            
            # Save detailed error message
            self.collection_task.status = 'failed'
            # Include full error message and traceback for debugging
            self.collection_task.error_message = f"{error_msg}\n\n{traceback_str[:1000]}"  # Limit traceback length
            self.collection_task.completed_at = datetime.utcnow()
            db.session.commit()
            raise
    
    def _collect_vmware_hosts(self, hosts: List[Host]):
        """Collect VMware hosts using platform API"""
        try:
            from prophet.collector.hosts.vmware import VMwareCollector
            
            # Create temp directory for collection
            temp_dir = tempfile.mkdtemp(prefix='vmware_collect_')
            
            try:
                # Refresh platform object to ensure we have latest data
                db.session.refresh(self.platform)
                
                # Get platform password - ensure it's loaded from database
                logger.info(f"Getting password for platform {self.platform.name} (ID: {self.platform.id})")
                logger.debug(f"Platform password_encrypted field exists: {self.platform.password_encrypted is not None}")
                
                password = self.platform.get_password()
                
                if password is None or password == '':
                    error_msg = (
                        f"Platform {self.platform.name} (ID: {self.platform.id}) password is not set or cannot be decrypted. "
                        f"password_encrypted field: {'exists' if self.platform.password_encrypted else 'missing'}. "
                        f"Please update the platform credentials in the platform management page."
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                logger.info(f"Password retrieved successfully for platform {self.platform.name}")
                
                # Connect to platform
                collector = VMwareCollector(
                    ip=self.platform.host,
                    username=self.platform.username,
                    password=password,  # Ensure password is a non-empty string
                    ssh_port=self.platform.port or 443,
                    key_path=None,
                    output_path=temp_dir,
                    os_type='VMWARE',
                )
                
                collector.connect()
                
                # Collect platform data once (collects all VMs from platform)
                # Then filter for only the hosts in this task
                logger.info(f"Collecting data from platform {self.platform.name} for {len(hosts)} selected hosts")
                collected_data = collector.collect()
                
                if not collected_data:
                    raise ValueError("No data collected from platform")
                
                # Extract VMs info from collected data
                root_key = list(collected_data.keys())[0] if collected_data else None
                if not root_key:
                    raise ValueError("Invalid collected data structure")
                
                results = collected_data[root_key].get('results', {})
                vms_info = results.get('vms', {})
                
                # Create a mapping of VM identifiers to VM data for quick lookup
                vm_map = {}
                for vmid, vm_info in vms_info.items():
                    vm_ip = vm_info.get('ipAddress', '')
                    vm_name = vm_info.get('name', '')
                    vm_uuid = vm_info.get('uuid', '')
                    # Index by IP, name, and UUID for quick lookup
                    if vm_ip:
                        vm_map[vm_ip] = vm_info
                    if vm_name:
                        vm_map[vm_name] = vm_info
                    if vm_uuid:
                        vm_map[vm_uuid] = vm_info
                
                # Process each selected host
                completed = 0
                failed = 0
                
                for host in hosts:
                    try:
                        # Find matching VM data
                        vm_data = None
                        # Try to match by IP first, then hostname, then MAC/UUID
                        if host.ip in vm_map:
                            vm_data = vm_map[host.ip]
                        elif host.hostname and host.hostname in vm_map:
                            vm_data = vm_map[host.hostname]
                        elif host.mac and host.mac in vm_map:
                            vm_data = vm_map[host.mac]
                        else:
                            # Fallback: iterate through all VMs to find match
                            for vmid, vm_info in vms_info.items():
                                vm_ip = vm_info.get('ipAddress', '')
                                vm_name = vm_info.get('name', '')
                                vm_uuid = vm_info.get('uuid', '')
                                
                                if (host.ip == vm_ip or 
                                    (host.hostname and host.hostname == vm_name) or 
                                    (host.mac and host.mac == vm_uuid)):
                                    vm_data = vm_info
                                    break
                        
                        if not vm_data:
                            logger.warning(f"VM not found in collected data for host {host.ip}")
                            failed += 1
                            self.update_progress(failed=failed)
                            continue
                        
                        # Parse and update host data
                        vm_data_for_parser = {
                            vm_data.get('name', host.hostname or host.ip): vm_data
                        }
                        collector_data_format = {
                            f"VMWARE_{host.ip}": {
                                "results": vm_data_for_parser,
                                "os_type": "VMWARE",
                                "tcp_ports": None
                            }
                        }
                        
                        parser_service = CollectionParserService('VMWARE')
                        parsed_data = parser_service.parse_collection_data(collector_data_format)
                        parser_service.update_host_from_parsed_data(host, parsed_data)
                        
                        # Update host metadata
                        host.source = 'platform'
                        host.source_platform_id = self.platform.id
                        host.virtualization_platform_id = self.platform.id
                        # Set status to collecting first, then completed
                        host.collection_status = 'collecting'
                        db.session.commit()  # Commit immediately for real-time updates
                        
                        # Update to completed
                        host.collection_status = 'completed'
                        host.last_collected_at = datetime.utcnow()
                        
                        # Record collection history
                        detail = HostDetail(
                            host_id=host.id,
                            details='',
                            status='success',
                            collection_method='vmware_platform',
                            collected_at=datetime.utcnow(),
                        )
                        db.session.add(detail)
                        
                        db.session.commit()
                        completed += 1
                        self.update_progress(completed=completed)
                        
                    except Exception as e:
                        logger.error(f"Error collecting host {host.ip}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        
                        host.collection_status = 'failed'
                        host.last_collected_at = datetime.utcnow()
                        
                        # Record failure with detailed error message
                        error_msg = str(e)
                        traceback_str = traceback.format_exc()
                        detail = HostDetail(
                            host_id=host.id,
                            details='',
                            status='failed',
                            collection_method='vmware_platform',
                            error_message=f"{error_msg}\n\n{traceback_str[:500]}",  # Limit traceback length
                            collected_at=datetime.utcnow(),
                        )
                        db.session.add(detail)
                        db.session.commit()
                        
                        failed += 1
                        self.update_progress(failed=failed)
                        continue
                
            finally:
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"VMware collection failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

