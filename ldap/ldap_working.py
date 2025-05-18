import ldap
import sys

# LDAP server settings
# LDAP_SERVER = "ldaps://192.168.178.50:636"  # Your server IP
LDAP_SERVER = "ldap://192.168.178.50:389"  # Your server IP
# LDAP_SERVER = "ldap://192.168.20.10:389"  # Your server IP
BIND_DN = "max.mustermann@mylab.local"  # Your full user logon name
PASSWORD = "FHKiel123!"  # User password
BASE_DN = "dc=mylab,dc=local"  # Correct BASE_DN for your domain
SEARCH_FILTER = "(userPrincipalName=max.mustermann@mylab.local)"  # Find the user with exactly that name combination
# sAMAccountName=mmustermann
# userPrincipalName=max.mustermann@mylab.local

# Attributs you want to get printed
ATTRIBUTES = ["givenName", "sn"]

try:
    # Connect and bind
    # ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    conn = ldap.initialize(LDAP_SERVER)
    conn.set_option(ldap.OPT_DEBUG_LEVEL, 255)
    conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)  # for LDAPv3
    conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)  # 5 seconds timeout
    conn.set_option(ldap.OPT_REFERRALS, 0)  # Important for AD: Disable referrals!

    # conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_DEMAND)
    # conn.set_option(ldap.OPT_X_TLS_CACERTFILE, "/path/to/cacert.pem")
    # conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    # conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
    # conn.set_option(ldap.OPT_X_TLS_DEMAND, True)
    # conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
    # conn.start_tls_s()

    print("username:", BIND_DN)
    print("password:", PASSWORD)

    try:
        conn.simple_bind_s(BIND_DN, PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        print("INVALID_CREDENTIALS")
        sys.exit()

    print("Successfully connected and bound to the LDAP server.")

    # Perform search
    result = conn.search_s(BASE_DN, ldap.SCOPE_SUBTREE, SEARCH_FILTER, ATTRIBUTES)
    print("Search results:")
    for dn, entry in result:
        if dn is None:
            continue  # skips LDAP references
        print(f"DN: {dn}")
        for attr, values in entry.items():
            for value in values:
                print(f"  {attr}: {value.decode('utf-8')}")  # to make it readable

    conn.unbind_s()

except ldap.LDAPError as e:
    print("LDAP error:", e)

# Notes Robert
# - followed tutorial (https://activedirectorypro.com/create-active-directory-test-environment/), but did NOT bulk import users
# - instead added single user: max.mustermann@mylab.local, password: FHKiel123!
# - set the VMs network to Host-only Adapter instead of internal network
# - in Virtualbox, under Tools at the top -> choose 'Network' -> Properties Tab -> Adapter Adress: 192.168.20.1, Adapter Mask: 255.255.255.0, DHCP Address: 192.168.20.15

# - to make pings working:
#       - set network to private in windows defender
#       - control panel -> firewall -> advanced settings -> inbound rules -> file sharing ICMP private
# - to make ad server on other device in network work:
#       - choose bridged adapter in VMs network settings, choose your network driver, check 'cable connected'
#       - a Host-only adapter in Virtualbox settings is not needed
#       - change the IP inside the windows server: access ethernet settings via control panel, adapter settings
#           - change IP from 192.168.20.10 to e.g. 192.168.178.50
#           - keep mask as 255.255.255.0
#           - default gateway: 192.168.178.1
#           - preferred DNS: 192.168.178.1
