"""PES WESYS zlib compression/decompression utilities."""

import struct
import zlib


class DecodeError(Exception):
    pass


def decode_header(byte_buffer: bytes) -> memoryview | None:
    """Check for WESYS header and return compressed data portion."""
    if len(byte_buffer) < 16:
        return None
    header = byte_buffer[0:16]
    (magic,) = struct.unpack("< 4x 4s 8x", header)
    if magic != b"ESYS":
        return None
    return memoryview(byte_buffer)[16:]


def is_compressed(byte_buffer: bytes) -> bool:
    """Check if buffer has WESYS compression header."""
    return decode_header(byte_buffer) is not None


def decompress(byte_buffer: bytes) -> bytes:
    """Decompress WESYS-compressed data. Raises DecodeError on failure."""
    compressed_buffer = decode_header(byte_buffer)
    if compressed_buffer is None:
        raise DecodeError("Not a WESYS compressed file")
    try:
        return zlib.decompress(compressed_buffer)
    except Exception as e:
        raise DecodeError(f"Decompression failed: {e}")


def try_decompress(byte_buffer: bytes) -> bytes:
    """Decompress if WESYS-compressed, otherwise return original."""
    compressed_buffer = decode_header(byte_buffer)
    if compressed_buffer is None:
        return byte_buffer
    try:
        return zlib.decompress(compressed_buffer)
    except Exception:
        raise DecodeError("Decompression failed")


def encode_header(compressed_buffer: bytes, uncompressed_buffer: bytes) -> bytes:
    """Create WESYS header for compressed data."""
    return struct.pack(
        "< 3B 5s II",
        0x00,
        0x10,
        0x01,
        "WESYS".encode("UTF-8"),
        len(compressed_buffer),
        len(uncompressed_buffer),
    )


def compress(byte_buffer: bytes) -> bytes:
    """Compress data with WESYS header."""
    compressed_buffer = zlib.compress(byte_buffer)
    return encode_header(compressed_buffer, byte_buffer) + compressed_buffer


def try_compress(byte_buffer: bytes) -> bytes:
    """Compress only if it results in smaller size."""
    compressed_buffer = zlib.compress(byte_buffer)
    if len(compressed_buffer) + 16 < len(byte_buffer):
        return encode_header(compressed_buffer, byte_buffer) + compressed_buffer
    return byte_buffer
