# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Alert management system"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    def send_alert(self, fault):
        """Send alert for detected fault"""
        if not self.enabled:
            return
        
        logger.warning(f"ALERT: {fault['type']} on circuit {fault['circuit_id']}")
        
        # Local alerts
        if self.config.get('local', {}).get('buzzer'):
            self._trigger_buzzer()
        
        # Email alerts
        if self.config.get('email', {}).get('enabled'):
            self._send_email(fault)
        
        # SMS alerts
        if self.config.get('sms', {}).get('enabled'):
            self._send_sms(fault)
    
    def _trigger_buzzer(self):
        """Trigger local buzzer"""
        logger.debug("Buzzer triggered")
        # GPIO buzzer control would go here
    
    def _send_email(self, fault):
        """Send email alert"""
        try:
            email_config = self.config['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config.get('recipients', []))
            msg['Subject'] = f"GridGuard Alert: {fault['type']}"
            
            body = f"""
            GridGuard-Pi5 Alert
            
            Fault Type: {fault['type']}
            Circuit: {fault['circuit_id']}
            Severity: {fault['severity']}
            Description: {fault['description']}
            Timestamp: {fault['timestamp']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            logger.info("Email alert sent")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def _send_sms(self, fault):
        """Send SMS alert"""
        logger.debug("SMS alert (not implemented)")
