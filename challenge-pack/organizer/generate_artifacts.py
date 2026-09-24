"""Generate deterministic participant files for the YIT CTF MVP.

Uses only the Python standard library. Run this file from its directory after
copying the pack, or use `python generate_artifacts.py` in place.
"""
from __future__ import annotations

import base64
import gzip
import json
import math
import py_compile
import struct
import zlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "artifacts"


def write(relative: str, data: str | bytes) -> Path:
    p = ART / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data.encode() if isinstance(data, str) else data)
    return p


def caesar(text: str, shift: int) -> str:
    out = []
    for c in text:
        if c.isalpha():
            a = ord("A" if c.isupper() else "a")
            out.append(chr((ord(c) - a + shift) % 26 + a))
        else:
            out.append(c)
    return "".join(out)


def vigenere(text: str, key: str) -> str:
    out, n = [], 0
    for c in text:
        if c.isalpha():
            a = ord("A" if c.isupper() else "a")
            out.append(chr((ord(c) - a + ord(key[n % len(key)].upper()) - 65) % 26 + a))
            n += 1
        else:
            out.append(c)
    return "".join(out)


def png_with_text(message: str) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    # A valid one-pixel RGB PNG with a tEXt metadata chunk.
    raw = b"\x00\x21\x58\x99"
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"tEXt", b"AnalystNote\x00" + message.encode()) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def pcap(records: list[bytes]) -> bytes:
    header = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    out = bytearray(header)
    for i, payload in enumerate(records):
        # Ethernet + IPv4 + UDP with a harmless payload; analyzers show the flag in UDP data.
        eth = b"\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x01\x08\x00"
        udp = struct.pack(">HHHH", 31337, 31338, 8 + len(payload), 0)
        ip_len = 20 + len(udp) + len(payload)
        ip = b"\x45\x00" + struct.pack(">H", ip_len) + b"\x00\x01\x00\x00\x40\x11\x00\x00" + b"\x0a\x00\x00\x01\x0a\x00\x00\x02"
        frame = eth + ip + udp + payload
        out += struct.pack("<IIII", 1_700_000_000 + i, 0, len(frame), len(frame)) + frame
    return bytes(out)


def main() -> None:
    ART.mkdir(exist_ok=True)
    # Crypto
    write("crypto/c1_last_message.txt", caesar("FLAG: YITCTF{shift_happens}", 7) + "\n")
    nested = base64.b64encode(base64.b64encode(b"YITCTF{base64_is_just_encoding}")).decode()
    write("crypto/c2_layers.txt", "Decode every layer until you reach the flag:\n" + nested + "\n")
    write("crypto/c3_broken_cipher.txt", "Ciphertext (key is a campus direction):\n" + vigenere("YITCTF{vigenere_needs_a_key}", "NORTH") + "\n")
    # n = 61*53; e=17; decrypting c yields 65, used as a shift key.
    write("crypto/c4_rsa.txt", "n = 3233\ne = 17\nc = 2790\n\nDecrypt c. Use the resulting integer as a Caesar shift to decrypt:\n" + caesar("YITCTF{rsa_small_primes_fail}", 65) + "\n")

    # Forensics
    write("forensics/f1_whats_in_the_image.png", png_with_text("YITCTF{pngs_can_talk}"))
    write("forensics/f2_metadata.jpg", b"\xff\xd8\xff\xe1" + b"Exif\x00\x00Artist=YIT Media Lab;Comment=YITCTF{metadata_matters}\n" + b"\xff\xd9")
    write("forensics/f3_packet_hunt.pcap", pcap([b"GET /status HTTP/1.1", b"note=look-at-udp-payload", b"YITCTF{packets_tell_stories}"]))
    with zipfile.ZipFile(ART / "forensics/f4_deleted_evidence.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("notes/readme.txt", "The incident report was moved, not erased.\n")
        z.writestr("recovered/.evidence.txt", "YITCTF{deleted_is_not_gone}\n")

    # Offline, fictional OSINT evidence. No real people or organizations are involved.
    write("osint/o1_find_the_place.html", """<!doctype html><title>Campus photo</title><h1>YIT Student Centre</h1><p>Photo ID 41.40338, 2.17403</p><p>Submit the city in lowercase with underscores.</p><!-- YITCTF{barcelona_from_coordinates} -->""")
    write("osint/o2_digital_footprints.html", """<title>Archive: @byte_baker</title><h1>@byte_baker</h1><p>My favourite transport is the underground. My first CTF was in 2017.</p><p>Archive tag: YITCTF{handles_leave_traces}</p>""")
    with zipfile.ZipFile(ART / "osint/o3_missing_developer.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("commit-log.txt", "a1c4  Add deploy note -- Aria M.\nbeef  Remove temporary token\n")
        z.writestr("docs/CONTRIBUTORS", "aria.m@fictional.yit.local\n")
        z.writestr(".git/config", "[remote \"origin\"]\n url = https://code.example.invalid/aria/orbit\n")
        z.writestr("README.txt", "Everything is fictional. The answer is in the contributor trail: YITCTF{aria_found_the_repo}\n")
    with zipfile.ZipFile(ART / "osint/o4_final_connection.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mail/one.txt", "Project codename: ORBIT\n")
        z.writestr("mail/two.txt", "The launch window is BLUE-7.\n")
        z.writestr("archive/final.txt", "Combine the two clues: YITCTF{orbit_blue_7}\n")

    # Reverse engineering: Python bytecode is portable and intentional for a beginner event.
    r1 = write("reverse/r1_strings_dont_lie.py", "banner='YIT CTF welcome'\nunused='YITCTF{strings_are_clues}'\nprint(banner)\n")
    py_compile.compile(str(r1), cfile=str(ART / "reverse/strings-dont-lie.pyc"))
    r1.unlink()
    r2 = write("reverse/r2_crack_the_code.py", """import sys\nTARGET=[44,60,33,54,33,51,14,13,26,7,42,28,6,42,7,16,3,16,7,6,28,23,25,16,8]\nKEY=117\ndef ok(s): return [ord(c)^KEY for c in s]==TARGET\nprint('correct' if len(sys.argv)>1 and ok(sys.argv[1]) else 'try again')\n# answer: YITCTF{xor_is_reversible}\n""")
    py_compile.compile(str(r2), cfile=str(ART / "reverse/crack-the-code.pyc"))
    r2.unlink()

    # Misc
    write("misc/m1_strange_file.dat", gzip.compress(base64.b64encode(b"YITCTF{magic_bytes_first}")))
    with zipfile.ZipFile(ART / "misc/m2_outside_the_box.zip", "w", zipfile.ZIP_DEFLATED) as outer:
        inner = ROOT / "_inner.zip"
        with zipfile.ZipFile(inner, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("not_a_decoy.txt", "YITCTF{there_is_always_another_layer}\n")
        outer.write(inner, "box/another_box.zip")
        outer.writestr("box/readme.txt", "A box can hold another box.\n")
        inner.unlink()

    print(f"Generated artifacts in {ART}")


if __name__ == "__main__":
    main()
