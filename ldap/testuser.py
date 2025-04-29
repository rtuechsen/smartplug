import ldap

# LDAP server settings
LDAP_SERVER = "ldap://192.168.20.10:389"  # Your server IP
BIND_DN = "test.user@mylab.local"          # Your full user logon name
PASSWORD = "FHKiel123!"                    # User password
BASE_DN = "dc=mylab,dc=local"               # Correct BASE_DN for your domain
SEARCH_FILTER = "(sAMAccountName=test.user)"      # Find the user with exactly that name combination

# Attributs you want to get printed
ATTRIBUTES = ["cn", "sAMAccountName", "userPrincipalName"]

try:
    # Connect and bind
    conn = ldap.initialize(LDAP_SERVER)
    conn.set_option(ldap.OPT_REFERRALS, 0)  # Important for AD: Disable referrals!
    conn.simple_bind_s(BIND_DN, PASSWORD)
    print("Successfully connected and bound to the LDAP server.")

    # Perform search
    result = conn.search_s(BASE_DN, ldap.SCOPE_SUBTREE, SEARCH_FILTER, ATTRIBUTES)
    print("Search results:")
    for dn, entry in result:
        if dn is None:
            continue # skips LDAP references
        print(f"DN: {dn}")
        for attr, values in entry.items():
            for value in values:
                print(f"  {attr}: {value.decode('utf-8')}") # to make it readable

    conn.unbind_s()
except ldap.LDAPError as e:
    print("LDAP error:", e)
