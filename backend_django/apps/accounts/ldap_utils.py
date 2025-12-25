"""
LDAP authentication utilities using ldap3 (pure Python, works on Windows)
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Check if ldap3 is available
LDAP_AVAILABLE = False

try:
    from ldap3 import Server, Connection, ALL, NONE, SUBTREE, Tls, NTLM
    from ldap3.core.exceptions import LDAPException, LDAPBindError, LDAPSocketOpenError
    import ssl
    LDAP_AVAILABLE = True
    logger.info("[LDAP] ldap3 is available")
except ImportError as e:
    logger.warning(f"[LDAP] ldap3 not installed: {e}. LDAP authentication will not work.")
    logger.warning("[LDAP] Install with: pip install ldap3")


class LDAPError(Exception):
    """LDAP authentication error"""
    pass


class LDAPAuthenticator:
    """LDAP authentication handler using ldap3"""

    def __init__(self):
        if not getattr(settings, 'LDAP_ENABLED', False):
            raise LDAPError("LDAP is not enabled")
        if not LDAP_AVAILABLE:
            raise LDAPError("ldap3 package is not installed. Install with: pip install ldap3")

        self.server_url = getattr(settings, 'LDAP_SERVER', 'ldap://localhost:389')
        self.base_dn = getattr(settings, 'LDAP_BASE_DN', '')
        self.bind_dn = getattr(settings, 'LDAP_USER_DN', '')
        self.bind_password = getattr(settings, 'LDAP_USER_PASSWORD', '')
        self.user_search_base = getattr(settings, 'LDAP_USER_SEARCH_BASE', '')
        self.user_search_filter = getattr(settings, 'LDAP_USER_SEARCH_FILTER', '(sAMAccountName={username})')
        self.group_search_base = getattr(settings, 'LDAP_GROUP_SEARCH_BASE', '')
        self.require_group = getattr(settings, 'LDAP_REQUIRE_GROUP', '')
        self.use_tls = getattr(settings, 'LDAP_USE_TLS', False)
        self.tls_ca_file = getattr(settings, 'LDAP_TLS_CA_FILE', '')

        # Timeouts (seconds) - tuned for UX; can be overridden via Django settings
        # ldap3 expects int for timeouts, not float or string
        def safe_int(value, default):
            """Safely convert value to int"""
            if value is None:
                return default
            try:
                return int(float(str(value)))
            except (ValueError, TypeError):
                return default
        
        self.connect_timeout = safe_int(getattr(settings, 'LDAP_CONNECT_TIMEOUT_SEC', None), 3)
        self.receive_timeout = safe_int(getattr(settings, 'LDAP_RECEIVE_TIMEOUT_SEC', None), 3)
        self.search_time_limit = safe_int(getattr(settings, 'LDAP_SEARCH_TIME_LIMIT_SEC', None), 5)
        
        # Parse server URL
        self._parse_server_url()
        
        logger.info(f"[LDAP] Initialized - Server: {self.host}:{self.port}, SSL: {self.use_ssl}")
        logger.debug(f"[LDAP] Base DN: {self.base_dn}")
        logger.debug(f"[LDAP] User Search Base: {self.user_search_base}")
        logger.debug(f"[LDAP] User Search Filter: {self.user_search_filter}")

    def _parse_server_url(self):
        """Parse server URL into components"""
        server = self.server_url
        self.use_ssl = False
        
        if server.startswith('ldaps://'):
            self.use_ssl = True
            server = server[8:]
            default_port = 636
        elif server.startswith('ldap://'):
            server = server[7:]
            default_port = 389
        else:
            default_port = 389
        
        # Parse host and port
        if ':' in server:
            self.host, port_str = server.split(':', 1)
            try:
                self.port = int(port_str)
            except ValueError:
                self.port = default_port
        else:
            self.host = server
            self.port = default_port

    def _get_server(self) -> 'Server':
        """Create LDAP server object"""
        tls_config = None
        
        if self.use_ssl or self.use_tls:
            tls_config = Tls(
                validate=ssl.CERT_NONE,  # For self-signed certs, change to CERT_REQUIRED for prod
                ca_certs_file=self.tls_ca_file if self.tls_ca_file else None
            )
        
        server = Server(
            self.host,
            port=self.port,
            use_ssl=self.use_ssl,
            tls=tls_config,
            # get_info=ALL triggers schema/DSA info queries and can noticeably slow login
            get_info=NONE,
            connect_timeout=self.connect_timeout,
        )
        
        return server

    def _get_domain_from_base_dn(self) -> str:
        """Extract domain from base DN (dc=company,dc=com -> company.com)"""
        domain_parts = []
        for part in self.base_dn.split(','):
            part = part.strip()
            if part.lower().startswith('dc='):
                domain_parts.append(part[3:])
        return '.'.join(domain_parts)

    def _get_netbios_domain(self) -> str:
        """Get NetBIOS domain name (first DC component, uppercase)"""
        for part in self.base_dn.split(','):
            part = part.strip()
            if part.lower().startswith('dc='):
                return part[3:].upper()
        return ''

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """
        Authenticate user against LDAP/Active Directory
        
        Args:
            username: Username to authenticate
            password: User password
            
        Returns:
            Dictionary with user info if successful, None otherwise
        """
        if not username or not password:
            logger.debug("[LDAP] Empty username or password")
            return None

        logger.info(f"[LDAP] Attempting authentication for user: {username}")
        t0 = time.perf_counter()

        t_server0 = time.perf_counter()
        server = self._get_server()
        logger.info(
            "[Perf][LDAP] step=server_create ms=%d username=%s",
            int((time.perf_counter() - t_server0) * 1000),
            username,
        )
        
        # Try multiple authentication strategies for Active Directory
        strategies = []
        
        # Strategy 1: UPN format (user@domain.com) - most common for AD
        domain = self._get_domain_from_base_dn()
        username_has_at = '@' in username
        username_has_slash = '\\' in username
        username_is_provided = username_has_at or username_has_slash
        if domain and not username_is_provided:
            strategies.append(('UPN', f"{username}@{domain}"))
        
        # Strategy 2: DOMAIN\username format
        netbios = self._get_netbios_domain()
        if netbios and not username_is_provided:
            strategies.append(('NETBIOS', f"{netbios}\\{username}"))
        
        # Strategy 3: If username already contains @ or \, use as-is
        if username_is_provided:
            strategies.insert(0, ('PROVIDED', username))
        
        # Try each strategy
        conn = None
        bind_success = False
        
        for strategy_name, bind_user in strategies:
            logger.debug(f"[LDAP] Trying {strategy_name} bind: {bind_user}")
            try:
                t_bind0 = time.perf_counter()
                conn = Connection(
                    server,
                    user=bind_user,
                    password=password,
                    auto_bind=True,
                    raise_exceptions=True,
                    receive_timeout=self.receive_timeout,
                )
                bind_success = True
                logger.info(f"[LDAP] {strategy_name} bind successful for: {username}")
                logger.info(
                    "[Perf][LDAP] step=bind strategy=%s ms=%d username=%s",
                    strategy_name,
                    int((time.perf_counter() - t_bind0) * 1000),
                    username,
                )
                break
            except LDAPBindError as e:
                logger.debug(f"[LDAP] {strategy_name} bind failed: Invalid credentials")
                logger.info(
                    "[Perf][LDAP] step=bind_failed strategy=%s ms=%d username=%s",
                    strategy_name,
                    int((time.perf_counter() - t_bind0) * 1000),
                    username,
                )
                continue
            except LDAPSocketOpenError as e:
                logger.error(f"[LDAP] Cannot connect to server: {e}")
                return None
            except LDAPException as e:
                logger.debug(f"[LDAP] {strategy_name} bind failed: {e}")
                logger.info(
                    "[Perf][LDAP] step=bind_error strategy=%s ms=%d username=%s",
                    strategy_name,
                    int((time.perf_counter() - t_bind0) * 1000),
                    username,
                )
                continue
            except Exception as e:
                logger.error(f"[LDAP] Unexpected error during {strategy_name} bind: {e}")
                logger.info(
                    "[Perf][LDAP] step=bind_exception strategy=%s ms=%d username=%s",
                    strategy_name,
                    int((time.perf_counter() - t_bind0) * 1000),
                    username,
                )
                continue

        if not bind_success:
            logger.info(f"[LDAP] All bind strategies failed for user: {username}")
            return None

        # Search for user attributes
        user_attrs = None
        user_dn = None
        
        try:
            t_search0 = time.perf_counter()
            # Extract username without domain for search (sAMAccountName doesn't include @domain)
            search_username = username.split('@')[0] if '@' in username else username
            search_username = search_username.split('\\')[-1]  # Remove domain\ prefix if present
            search_filter = self.user_search_filter.replace('{username}', search_username)
            search_base = self.user_search_base or self.base_dn
            
            logger.debug(f"[LDAP] Searching for user attributes: base={search_base}, filter={search_filter}")
            
            conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                time_limit=self.search_time_limit,
                attributes=[
                    'cn', 'mail', 'uid', 'sAMAccountName', 
                    'givenName', 'sn', 'memberOf', 'displayName',
                    'userPrincipalName', 'distinguishedName'
                ]
            )
            logger.info(
                "[Perf][LDAP] step=search_user ms=%d username=%s entries=%d",
                int((time.perf_counter() - t_search0) * 1000),
                username,
                len(conn.entries or []),
            )
            
            if conn.entries:
                entry = conn.entries[0]
                user_dn = str(entry.entry_dn)
                user_attrs = entry.entry_attributes_as_dict
                logger.debug(f"[LDAP] Found user DN: {user_dn}")
                logger.debug(f"[LDAP] User attributes: {list(user_attrs.keys())}")
        except LDAPException as e:
            logger.warning(f"[LDAP] Could not fetch user attributes: {e}")
        except Exception as e:
            logger.warning(f"[LDAP] Error fetching user attributes: {e}")

        # Check group membership if required
        if self.require_group and user_attrs:
            if not self._check_group_membership(user_attrs):
                logger.info(f"[LDAP] User {username} is not in required group: {self.require_group}")
                try:
                    conn.unbind()
                except:
                    pass
                return None

        # Build user info
        user_info = {
            'username': username,
            'dn': user_dn or username,
            'email': self._get_attr(user_attrs, 'mail', f'{username}@{domain}' if domain else f'{username}@local'),
            'full_name': self._get_full_name(user_attrs, username),
            'groups': self._get_groups(user_attrs),
        }

        try:
            conn.unbind()
        except:
            pass
            
        logger.info(f"[LDAP] Authentication successful for: {username}")
        logger.debug(f"[LDAP] User info: {user_info}")
        logger.info(
            "[Perf][LDAP] step=total ms=%d username=%s",
            int((time.perf_counter() - t0) * 1000),
            username,
        )
        return user_info

    def _get_attr(self, attrs: Optional[dict], key: str, default: str = '') -> str:
        """Get attribute value from LDAP attributes"""
        if not attrs or key not in attrs:
            return default
        values = attrs.get(key, [])
        if values and len(values) > 0:
            return str(values[0])
        return default

    def _get_full_name(self, attrs: Optional[dict], username: str) -> str:
        """Get full name from LDAP attributes"""
        if not attrs:
            return username
            
        # Try displayName first (common in AD)
        display_name = self._get_attr(attrs, 'displayName', '')
        if display_name:
            return display_name
            
        # Try cn
        cn = self._get_attr(attrs, 'cn', '')
        if cn:
            return cn
        
        # Try givenName + sn
        given_name = self._get_attr(attrs, 'givenName', '')
        sn = self._get_attr(attrs, 'sn', '')
        if given_name and sn:
            return f"{given_name} {sn}"
        if given_name:
            return given_name
        if sn:
            return sn
        
        return username

    def _get_groups(self, attrs: Optional[dict]) -> list:
        """Get group memberships from LDAP attributes"""
        groups = []
        if not attrs or 'memberOf' not in attrs:
            return groups
            
        for group_dn in attrs.get('memberOf', []):
            group_dn = str(group_dn)
            # Extract CN from DN (CN=GroupName,OU=Groups,DC=domain,DC=com)
            parts = group_dn.split(',')
            for part in parts:
                if part.upper().startswith('CN='):
                    groups.append(part[3:])
                    break
        return groups

    def _check_group_membership(self, user_attrs: dict) -> bool:
        """Check if user is member of required group"""
        if not self.require_group:
            return True

        member_of = user_attrs.get('memberOf', [])
        required_group_lower = self.require_group.lower()
        
        for group_dn in member_of:
            group_dn = str(group_dn).lower()
            if required_group_lower in group_dn:
                return True

        return False


def authenticate_ldap(username: str, password: str) -> Optional[dict]:
    """
    Authenticate user using LDAP
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User info dict if successful, None otherwise
    """
    if not getattr(settings, 'LDAP_ENABLED', False):
        logger.debug("[LDAP] LDAP is not enabled in settings")
        return None
    
    if not LDAP_AVAILABLE:
        logger.error("[LDAP] ldap3 is not installed. Install with: pip install ldap3")
        return None
    
    try:
        authenticator = LDAPAuthenticator()
        return authenticator.authenticate(username, password)
    except LDAPError as e:
        logger.error(f"[LDAP] Configuration error: {e}")
        return None
    except Exception as e:
        logger.error(f"[LDAP] Unexpected error: {e}", exc_info=True)
        return None
