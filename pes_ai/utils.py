from struct import pack, unpack


def conv_from_bytes(byte_data: bytes) -> int | float:
    p = unpack("<i", byte_data)[0]
    if p > 10000 or p < 0:
        p = round(unpack("<f", byte_data)[0], 3)
    return p


def conv_to_bytes(value: int | float | bool | None) -> bytes:
    match type(value).__name__:
        case "int":
            return pack("<i", value)
        case "float":
            return pack("<f", value)
        case "bool":
            return pack("?", value)
        case "NoneType":
            return pack("x")
