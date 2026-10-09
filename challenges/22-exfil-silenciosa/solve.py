#!/usr/bin/env python3
"""Solve EvilSec #22: recover the exfiltrated flag from the PCAP.

Flow:
1. Extract the SSLKEYLOGFILE attachment from SMTP stream 7.
2. Use tshark with that keylog to follow the decrypted DNS-over-TLS stream.
3. Sort suspicious base32 DNS labels by DNS transaction ID.
4. Decode the reconstructed encrypted ZIP and open it with the HTTP config password.
"""
from __future__ import annotations

import base64
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCAP = ROOT / "captura.pcapng"
PASSWORD = base64.b64decode("QzItS3I0azNuIzIwMjYh")  # HTTP heartbeat config
FLAG_RE = re.compile(rb"EVIL\{[^}\r\n]+\}")


def tshark(*args: str) -> str:
    return subprocess.run(
        ["tshark", "-r", str(PCAP), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def extract_keylog() -> bytes:
    stream = tshark("-q", "-z", "follow,tcp,ascii,7")
    match = re.search(
        r'filename="trace_output\.dat"\n\n(?P<body>.+?)\n------=_Part_002--',
        stream,
        re.S,
    )
    if not match:
        raise RuntimeError("SMTP trace_output.dat attachment not found")

    encoded = "".join(
        line.strip()
        for line in match.group("body").splitlines()
        if line.strip() and not line.startswith("\t")
    )
    return base64.b64decode(encoded)


def dns_query_chunks(keylog_path: Path) -> list[tuple[int, str]]:
    raw = tshark(
        "-o",
        f"tls.keylog_file:{keylog_path}",
        "-q",
        "-z",
        "follow,tls,raw,0",
    )
    chunks: list[tuple[int, str]] = []
    for line in raw.splitlines():
        # Client-side DNS-over-TLS queries are printed as tab-indented hex blobs.
        if not line.startswith("\t"):
            continue
        hex_blob = line.strip()
        if not re.fullmatch(r"[0-9a-f]+", hex_blob):
            continue

        record = bytes.fromhex(hex_blob)
        if len(record) < 14:
            continue
        msg_len = int.from_bytes(record[:2], "big")
        msg = record[2:]
        if len(msg) != msg_len or len(msg) < 12:
            continue

        txid = int.from_bytes(msg[:2], "big")
        flags = int.from_bytes(msg[2:4], "big")
        qdcount = int.from_bytes(msg[4:6], "big")
        if flags & 0x8000 or qdcount < 1:
            continue

        pos = 12
        labels: list[str] = []
        while pos < len(msg):
            size = msg[pos]
            pos += 1
            if size == 0:
                break
            if size & 0xC0:
                break
            labels.append(msg[pos : pos + size].decode("ascii"))
            pos += size

        qname = ".".join(labels)
        if qname.endswith(".cdn-sync.io") or qname.endswith(".stats-collector.net"):
            chunks.append((txid, labels[0]))
    return chunks


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        keylog_path = Path(tmp) / "sslkeylog.txt"
        keylog_path.write_bytes(extract_keylog())

        chunks = dns_query_chunks(keylog_path)
        if not chunks:
            raise RuntimeError("no suspicious DNS-over-TLS chunks found")

        encoded = "".join(label for _, label in sorted(chunks)).upper()
        archive = base64.b32decode(encoded + "=" * ((8 - len(encoded) % 8) % 8))
        zip_path = Path(tmp) / "exfil.zip"
        zip_path.write_bytes(archive)

        with zipfile.ZipFile(zip_path) as zf:
            flag_data = zf.read("flag.txt", pwd=PASSWORD)

    match = FLAG_RE.search(flag_data)
    if not match:
        raise RuntimeError("flag.txt did not contain an EVIL flag")
    print(match.group(0).decode())


if __name__ == "__main__":
    main()
