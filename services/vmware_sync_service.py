# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Service for syncing VMware platform resources to database"""

import logging
from typing import Dict, List
from datetime import datetime

from models import Host, HostDetail, VirtualizationPlatform, db
from utils.jwt import get_current_user_id

logger = logging.getLogger(__name__)


class VMwareSyncService:
    """Service for syncing VMware resources to database"""
    
    def __init__(self, platform: VirtualizationPlatform, user_id: int = None):
        """Initialize sync service"""
        self.platform = platform
        self.user_id = user_id or get_current_user_id()
        self.synced_count = 0
        self.updated_count = 0
        self.failed_count = 0
        self.failed_items = []  # Track failed items with details
    
    def sync_from_collector(self, collector, collected_data=None) -> Dict:
        """Sync resources from VMwareCollector to database
        
        Args:
            collector: VMwareCollector instance (already called collect())
            collected_data: Optional collected data dict (if None, will get from collector.collect() return value)
        """
        try:
            # Get collected data from collector if not provided
            if collected_data is None:
                # Call collect() to get data (returns dict, no YAML file)
                collected_data = collector.collect()
            
            if not collected_data:
                logger.error("No collected data available from collector")
                return {
                    'synced': 0,
                    'updated': 0,
                    'failed': 0,
                    'total': 0
                }
            
            # Extract data from collected_data structure
            # Structure: {root_key: {results: {server_info: ..., vms: ...}, os_type: ..., tcp_ports: ...}}
            root_key = list(collected_data.keys())[0] if collected_data else None
            if not root_key:
                logger.error("Invalid collected data structure")
                return {
                    'synced': 0,
                    'updated': 0,
                    'failed': 0,
                    'total': 0
                }
            
            results = collected_data[root_key].get('results', {})
            server_info = results.get('server_info', {})
            vms_info = results.get('vms', {})
            
            # Get ESXi hosts from server_info
            esxi_hosts = []
            if isinstance(server_info, dict):
                # If vCenter, server_info contains vCenter info with esxi nested
                if 'esxi' in server_info:
                    # vCenter case
                    esxis = server_info['esxi']
                    for esxi_name, esxi_info in esxis.items():
                        esxi_hosts.append({
                            'name': esxi_name,
                            'info': esxi_info
                        })
                else:
                    # ESXi case - server_info is the ESXi info itself
                    for esxi_name, esxi_info in server_info.items():
                        esxi_hosts.append({
                            'name': esxi_name,
                            'info': esxi_info
                        })
            
            # Get VMs from vms_info
            vms = []
            if isinstance(vms_info, dict):
                for vmid, vm_data in vms_info.items():
                    if isinstance(vm_data, dict):
                        vms.append(vm_data)
            
            # Sync ESXi hosts
            for esxi in esxi_hosts:
                self._sync_esxi_host(esxi)
            
            # Sync VMs
            for vm_data in vms:
                self._sync_vm(vm_data)
            
            db.session.commit()
            
            return {
                'synced': self.synced_count,
                'updated': self.updated_count,
                'failed': self.failed_count,
                'total': self.synced_count + self.updated_count,
                'failed_items': self.failed_items
            }
        except Exception as e:
            logger.error(f"VMware sync failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.session.rollback()
            raise
    
    def _get_data_from_collector(self, collector) -> Dict:
        """Get collected data from collector's internal state"""
        # Try to get from collector's internal attributes
        data = {}
        root_key = collector.root_key if hasattr(collector, 'root_key') else None
        
        if hasattr(collector, '_vc_info') and collector._vc_info:
            # vCenter case
            data[root_key] = {
                'results': {
                    'server_info': collector._vc_info,
                    'vms': collector._vms_info if hasattr(collector, '_vms_info') else {}
                },
                'os_type': collector.os_type if hasattr(collector, 'os_type') else 'VMWARE',
                'tcp_ports': None
            }
        elif hasattr(collector, '_esxis_info') and collector._esxis_info:
            # ESXi case
            data[root_key] = {
                'results': {
                    'server_info': collector._esxis_info,
                    'vms': collector._vms_info if hasattr(collector, '_vms_info') else {}
                },
                'os_type': collector.os_type if hasattr(collector, 'os_type') else 'VMWARE',
                'tcp_ports': None
            }
        
        return data
    
    
    def _sync_esxi_host(self, esxi: Dict):
        """Sync ESXi host to database"""
        try:
            esxi_name = esxi['name']
            esxi_info = esxi['info']
            
            # Extract ESXi summary info
            esxi_summary = esxi_info.get('esxi_info', {}) if isinstance(esxi_info, dict) else esxi_info
            
            # Extract IP and hardware info
            ip = (esxi_summary.get('ip') or 
                  esxi_summary.get('managementIp') or 
                  esxi_summary.get('hostname') or 
                  esxi_name)
            
            # Try to find existing host by name or IP
            host = Host.query.filter(
                ((Host.hostname == esxi_name) | (Host.ip == ip)) &
                (Host.deleted_at == None)
            ).first()
            
            # Extract hardware info
            cpu_cores = (esxi_summary.get('numCpu') or 
                        esxi_summary.get('cpuCores') or 
                        esxi_summary.get('numCpuThreads'))
            memory_bytes = (esxi_summary.get('memorySize') or 
                           esxi_summary.get('totalMemory'))
            memory_gb = memory_bytes / (1024 * 1024 * 1024) if memory_bytes else None
            
            if host:
                # Update existing host
                host.hostname = esxi_name
                if ip and ip != host.ip:
                    host.ip = ip
                host.os_type = 'vmware'
                host.device_type = 'host'
                host.is_physical = False
                host.virtualization_platform_id = self.platform.id
                host.cpu_cores = cpu_cores
                host.memory_total = memory_gb
                host.updated_at = datetime.utcnow()
                self.updated_count += 1
            else:
                # Create new host
                host = Host(
                    hostname=esxi_name,
                    ip=ip,
                    os_type='vmware',
                    device_type='host',
                    is_physical=False,
                    virtualization_platform_id=self.platform.id,
                    cpu_cores=cpu_cores,
                    memory_total=memory_gb,
                    created_by=self.user_id,
                )
                db.session.add(host)
                db.session.flush()  # Get host.id
                self.synced_count += 1
            
            # Set source information
            host.source = 'platform'
            host.source_platform_id = self.platform.id
            
            # Record collection history (no longer storing raw JSON)
            detail = HostDetail(
                host_id=host.id,
                details='',  # No longer storing raw data
                status='success',
                collection_method='vmware_esxi',
                collected_at=datetime.utcnow(),
            )
            db.session.add(detail)
            
        except Exception as e:
            esxi_name = esxi.get('name', 'unknown')
            error_msg = str(e)
            logger.error(f"Failed to sync ESXi host {esxi_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.failed_count += 1
            self.failed_items.append({
                'type': 'esxi',
                'name': esxi_name,
                'ip': esxi.get('info', {}).get('ip') or esxi.get('info', {}).get('managementIp') or esxi_name,
                'error': error_msg
            })
    
    def _sync_vm(self, vm_info: Dict):
        """Sync VM to database using Parser"""
        try:
            vm_name = vm_info.get('name', '')
            vm_uuid = vm_info.get('uuid', '')
            
            if not vm_name:
                logger.warning("VM info missing name, skipping")
                self.failed_count += 1
                return
            
            # Prepare VM data in format expected by CollectionParserService
            # CollectionParserService expects: {root_key: {results: {...}, os_type: ...}}
            # VMwareParser expects: {vm_name: {esxi_host: {...}, name, memoryMB, numCpu, ...}}
            # So we wrap vm_info in the expected format
            vm_data_for_parser = {
                vm_name: vm_info
            }
            collector_data_format = {
                f"VMWARE_{vm_name}": {
                    "results": vm_data_for_parser,
                    "os_type": "VMWARE",
                    "tcp_ports": None
                }
            }
            
            # Use Parser to parse VM data
            from services.collection_parser_service import CollectionParserService
            parser_service = CollectionParserService('VMWARE')
            parsed_data = parser_service.parse_collection_data(collector_data_format)
            
            # Get IP from parsed data or vm_info
            vm_ip = parsed_data.get('basic', {}).get('conn_ip') or vm_info.get('ipAddress', '')
            if not vm_ip:
                # Try to get from network info
                network_info = vm_info.get('network', {})
                for net in network_info.values():
                    if net.get('ipAddress'):
                        vm_ip = net['ipAddress']
                        break
            
            # Try to find existing host by multiple criteria
            host = None
            
            # First, try to find by IP (most reliable)
            if vm_ip and vm_ip != vm_uuid and not vm_ip.startswith('vm-'):
                host = Host.query.filter_by(ip=vm_ip, deleted_at=None).first()
            
            # If not found, try by hostname
            if not host and vm_name:
                host = Host.query.filter_by(hostname=vm_name, deleted_at=None).first()
            
            # If not found, try by UUID (stored in mac field)
            if not host and vm_uuid:
                host = Host.query.filter_by(mac=vm_uuid, deleted_at=None).first()
            
            # If still not found, check if IP is a valid format (not UUID or vm- prefix)
            # and if it already exists (might be from scan)
            if not host and vm_ip:
                # Check if IP already exists (even if deleted_at is set, we might want to restore it)
                existing_by_ip = Host.query.filter_by(ip=vm_ip).first()
                if existing_by_ip:
                    # If exists but deleted, restore it
                    if existing_by_ip.deleted_at:
                        existing_by_ip.deleted_at = None
                    host = existing_by_ip
            
            if not host:
                # Use VM UUID or name as identifier if no valid IP
                if not vm_ip or vm_ip == vm_uuid or vm_ip.startswith('vm-'):
                    # Generate a unique IP-like identifier
                    vm_ip = f"vm-{vm_uuid[:8]}" if vm_uuid else f"vm-{vm_name}"
                
                # Double-check the IP doesn't exist before creating
                existing = Host.query.filter_by(ip=vm_ip, deleted_at=None).first()
                if existing:
                    host = existing
                else:
                    # Create new host
                    host = Host(
                        hostname=vm_name,
                        ip=vm_ip,
                        mac=vm_uuid,  # Use UUID as MAC for unique identification
                        source='platform',
                        source_platform_id=self.platform.id,
                        virtualization_platform_id=self.platform.id,
                        created_by=self.user_id,
                    )
                    db.session.add(host)
                    try:
                        db.session.flush()  # Get host.id
                        self.synced_count += 1
                    except Exception as e:
                        # If flush fails due to unique constraint, try to find existing
                        db.session.rollback()
                        existing = Host.query.filter_by(ip=vm_ip, deleted_at=None).first()
                        if existing:
                            host = existing
                            self.updated_count += 1
                        else:
                            raise
            else:
                # Update existing host
                self.updated_count += 1
            
            # Update host from parsed data (this will update all fields including disks, partitions, networks)
            parser_service.update_host_from_parsed_data(host, parsed_data)
            
            # Ensure source is set
            host.source = 'platform'
            host.source_platform_id = self.platform.id
            host.virtualization_platform_id = self.platform.id
            
            # Record collection history (no longer storing raw JSON)
            detail = HostDetail(
                host_id=host.id,
                details='',  # No longer storing raw data
                status='success',
                collection_method='vmware_vm',
                collected_at=datetime.utcnow(),
            )
            db.session.add(detail)
            
        except Exception as e:
            vm_name = vm_info.get('name', 'unknown')
            vm_ip = vm_info.get('ipAddress', '')
            error_msg = str(e)
            logger.error(f"Failed to sync VM {vm_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.failed_count += 1
            self.failed_items.append({
                'type': 'vm',
                'name': vm_name,
                'ip': vm_ip,
                'error': error_msg
            })

