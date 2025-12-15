from securevault.supabase_client import get_supabase
import datetime

class AuditLogger:
    @staticmethod
    def log(operation_type: str, user_identifier: str = None, details: dict = None, ip: str = None):
        """
        Logs an operation to the audit_logs table.
        
        Args:
            operation_type (str): The type of operation (e.g., 'KEY_GENERATION').
            user_identifier (str): Identifier for the user (optional).
            details (dict): Additional details about the operation.
            ip (str): IP address of the requester. If None, valid Flask request context is used.
        """
        
        # Auto-detect IP if in Flask context and not provided
        if not ip:
            try:
                from flask import request
                if request:
                     # Check for X-Forwarded-For header (common in proxies/Render)
                    if request.headers.getlist("X-Forwarded-For"):
                        ip = request.headers.getlist("X-Forwarded-For")[0]
                    else:
                        ip = request.remote_addr
            except ImportError:
                pass
            except RuntimeError:
                # Outside of request context
                pass

        data = {
            'operation_type': operation_type,
            'user_identifier': user_identifier,
            'details': details or {},
            'ip': ip,
            # 'timestamp' is handled by default now() in Postgres
        }
        
        try:
            get_supabase().table('audit_logs').insert(data).execute()
        except Exception as e:
            # We don't want audit logging failure to crash the main app, 
            # but in a high-security context, we might want to alert.
            # For now, print to stderr.
            print(f"AUDIT LOGGING FAILED: {str(e)}")
