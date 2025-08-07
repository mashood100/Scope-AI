import imaplib
import email
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from email.header import decode_header

logger = logging.getLogger(__name__)


class GmailService:
    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.connection = None
    
    def connect(self) -> bool:
        try:
            logger.info(f"🔗 Connecting to {self.imap_server}:{self.imap_port}")
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            logger.info(f"🔐 Logging in with email: {self.email_address}")
            self.connection.login(self.email_address, self.app_password)
            logger.info(f"✅ Successfully connected to Gmail")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"❌ IMAP authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to Gmail: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from Gmail")
            except Exception as e:
                logger.warning(f"Error during disconnection: {e}")
    
    def _decode_header_value(self, header_value: str) -> str:
        try:
            if header_value is None:
                return ""
            
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string.strip()
        except Exception as e:
            logger.warning(f"Failed to decode header '{header_value}': {e}")
            return str(header_value) if header_value else ""
    
    def check_group_messages(self, group_email: str, hours_back: int = 24) -> List[Dict[str, str]]:
        messages = []
        
        if not self.connection:
            if not self.connect():
                return messages
        
        try:
            # Select inbox
            result, data = self.connection.select('inbox')
            if result == 'OK':
                logger.info(f"✅ Inbox selected. Total messages: {data[0].decode()}")
            else:
                logger.error(f"❌ Failed to select inbox: {result}")
                return messages
            
            # Calculate date for search
            since_date = datetime.now() - timedelta(hours=hours_back)
            search_date = since_date.strftime("%d-%b-%Y")
            
            # Search for messages
            search_criteria = f'(FROM "{group_email}" SINCE "{search_date}")'
            logger.info(f"🔍 Searching: {search_criteria}")
            
            result, message_numbers = self.connection.search(None, search_criteria)
            
            if result != 'OK':
                logger.error(f"❌ Search failed: {result}")
                return messages
            
            message_ids = message_numbers[0].split()
            logger.info(f"📬 Found {len(message_ids)} messages from {group_email}")
            
            # Process messages
            for msg_id in message_ids:
                try:
                    result, msg_data = self.connection.fetch(msg_id, '(RFC822)')
                    
                    if result != 'OK':
                        logger.warning(f"Failed to fetch message {msg_id}")
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    message_info = {
                        'subject': self._decode_header_value(email_message.get('subject', '')),
                        'sender': self._decode_header_value(email_message.get('from', '')),
                        'date': email_message.get('date', ''),
                        'message_id': email_message.get('message-id', ''),
                        'group_email': group_email
                    }
                    
                    messages.append(message_info)
                    logger.debug(f"Processed message: {message_info['subject'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error while checking messages: {e}")
        
        return messages


def test_gmail_connection(email_address: str, app_password: str) -> bool:
    logger.info("🧪 🧪 🧪 Testing Gmail connection 🧪 🧪 🧪 ")
    gmail_service = GmailService(email_address, app_password)
    
    try:
        if gmail_service.connect():
            result, data = gmail_service.connection.select('inbox')
            if result == 'OK':
                logger.info(f"✅ Connection test successful! Inbox has {data[0].decode()} messages")
                return True
            else:
                logger.error(f"❌ Failed to select inbox: {result}")
                return False
        else:
            return False
    except Exception as e:
        logger.error(f"❌ Connection test error: {e}")
        return False
    finally:
        gmail_service.disconnect()


def check_gmail_group_messages(email_address: str, app_password: str, 
                              group_email: str, hours_back: int = 24) -> List[Dict[str, str]]:
    gmail_service = GmailService(email_address, app_password)
    
    try:
        messages = gmail_service.check_group_messages(group_email, hours_back)
        return messages
    except Exception as e:
        logger.error(f"Error checking Gmail messages: {e}")
        return []
    finally:
        gmail_service.disconnect()


def check_gmail_from_settings(group_email: str, hours_back: int = 24) -> List[Dict[str, str]]:
    try:
        # Replace with actual email and app password
        # Generate app password from: https://myaccount.google.com/apppasswords
        email_address = "mashooddemo2@gmail.com"
        app_password = "five xtjd zadsdaus"

        if not test_gmail_connection(email_address, app_password):
            logger.error("❌ Connection test failed, aborting Gmail check")
            return []
        
        return check_gmail_group_messages(email_address, app_password, group_email, hours_back)
    
    except Exception as e:
        logger.error(f"Error checking Gmail: {e}")
        return []

