from puyapy import (
    Bytes,
    UInt64,
    bzero,
    extract,
    extract_uint16,
    getbit,
    itob,
    replace,
    setbit_bytes,
    subroutine,
    substring,
    urange,
)


@subroutine
def dynamic_array_pop_bit(source: Bytes) -> tuple[Bytes, Bytes]:
    """
    Pop the last item from an arc4 dynamic array of arc4 encoded boolean items

    source: The bytes for the source array

    returns: tuple of (The popped item, The updated bytes for the source array)
    """
    array_length = extract_uint16(source, 0)
    length_minus_1 = array_length - 1
    source = replace(source, 0, substring(itob(length_minus_1), 6, 8))
    popped_location = length_minus_1 + 16
    popped = setbit_bytes(Bytes(b"\x00"), 0, getbit(source, popped_location))
    source = setbit_bytes(source, popped_location, 0)
    source = substring(source, 0, 2 + ((length_minus_1 + 7) // 8))
    return popped, source


@subroutine
def dynamic_array_pop_fixed_size(source: Bytes, fixed_byte_size: UInt64) -> tuple[Bytes, Bytes]:
    """
    Pop the last item from an arc4 dynamic array of fixed sized items

    source: The bytes for the source array

    returns: tuple of (The popped item, The updated bytes for the source array)
    """
    array_length = extract_uint16(source, 0)
    length_minus_1 = array_length - 1
    source = replace(source, 0, substring(itob(length_minus_1), 6, 8))
    item_location = source.length - fixed_byte_size
    popped = extract(source, item_location, fixed_byte_size)
    source = substring(source, 0, item_location)
    return popped, source


@subroutine
def dynamic_array_pop_variable_size(source: Bytes) -> tuple[Bytes, Bytes]:
    """
    Pop the last item from an arc4 dynamic array of variably sized items

    source: The bytes for the source array

    returns: tuple of (The popped item, The updated bytes for the source array)
    """
    array_length = extract_uint16(source, 0)
    length_minus_1 = array_length - 1
    data_sans_header = substring(source, 2, source.length)
    popped_header_offset = length_minus_1 * 2
    popped_header = extract_uint16(data_sans_header, popped_header_offset)

    popped = substring(data_sans_header, popped_header, data_sans_header.length)
    data_sans_header = substring(data_sans_header, 0, popped_header_offset) + substring(
        data_sans_header, popped_header_offset + 2, popped_header
    )

    updated = substring(itob(length_minus_1), 6, 8) + recalculate_array_offsets_static(
        array_data=data_sans_header, length=length_minus_1, start_at_index=UInt64(0)
    )

    return popped, updated


@subroutine
def dynamic_array_concat_bits(
    *, source: Bytes, new_items_bytes: Bytes, new_items_count: UInt64, is_packed: bool
) -> Bytes:
    """
    Concat data to an arc4 dynamic array of arc4 encoded boolean values

    source: The bytes for the source array
    new_items_bytes: Either the data portion of an arc4 packed array of booleans
                        or
                     a sparse array of concatenated arc4 booleans
    new_items_count: The count of new items being added
    is_packed: True if new_items_bytes represents a packed array, else False

    returns: The updated bytes for the source array
    """
    array_length = extract_uint16(source, 0)
    source = replace(source, 0, substring(itob(array_length + new_items_count), 6, 8))
    current_bytes = (array_length + 7) // 8
    required_bytes = (array_length + 7 + new_items_count) // 8
    if current_bytes < required_bytes:
        source += bzero(required_bytes - current_bytes)

    write_offset = array_length + 16
    for i in urange(0, new_items_count, UInt64(1) if is_packed else UInt64(8)):
        source = setbit_bytes(source, write_offset, getbit(new_items_bytes, i))
        write_offset += 1

    return source


@subroutine
def dynamic_array_replace_variable_size(source: Bytes, new_item: Bytes, index: UInt64) -> Bytes:
    """
    Replace a single item in an arc4 dynamic array of variably sized items

    source: The bytes of the source array
    new_item: The bytes of the new item to be inserted
    index: The index to insert the new item at
    array_length: The length of the array

    returns: The updated bytes for the source array
    """
    array_length = extract_uint16(source, 0)
    return substring(source, 0, 2) + static_array_replace_variable_size(
        source=substring(source, 2, source.length),
        new_item=new_item,
        index=index,
        array_length=array_length,
    )


@subroutine
def static_array_replace_variable_size(
    source: Bytes, new_item: Bytes, index: UInt64, array_length: UInt64
) -> Bytes:
    """
    Replace a single item in an arc4 static array of variably sized items

    source: The bytes of the source array
    new_item: The bytes of the new item to be inserted
    index: The index to insert the new item at
    array_length: The length of the array

    returns: The updated bytes for the source array
    """
    assert index < array_length, "Index out of bounds"
    offset_for_index = extract_uint16(source, index * 2)
    old_item_length = extract_uint16(source, offset_for_index)
    old_item_end = offset_for_index + old_item_length + 2
    return recalculate_array_offsets_static(
        array_data=substring(source, 0, offset_for_index)
        + new_item
        + substring(source, old_item_end, source.length),
        length=array_length,
        start_at_index=index,
    )


@subroutine
def dynamic_array_concat_variable_size(
    source: Bytes, new_items_bytes: Bytes, new_items_count: UInt64
) -> Bytes:
    """
    Concat new items to an arc4 dynamic array of variably sized items

    source: The bytes of the source array
    new_items_bytes: The bytes for all new items, concatenated
    new_items_counts: The count of new items being added

    returns: The updated bytes for the source array
    """
    array_length = extract_uint16(source, 0)
    new_length = array_length + new_items_count
    header_end = array_length * 2 + 2

    return substring(itob(new_length), 6, 8) + recalculate_array_offsets_static(
        array_data=(
            substring(source, 2, header_end)
            + bzero(new_items_count * 2)
            + substring(source, header_end, source.length)
            + new_items_bytes
        ),
        length=new_length,
        start_at_index=UInt64(0),
    )


@subroutine
def dynamic_array_concat_fixed_size(
    source: Bytes, new_items_bytes: Bytes, new_items_count: UInt64
) -> Bytes:
    """
    Concat new items to an arc4 dynamic array of fixed sized items

    source: The bytes of the source array
    new_items_bytes: The bytes for all new items, concatenated
    new_items_counts: The count of new items being added

    returns: The updated bytes for the source array
    """
    array_length = extract_uint16(source, 0)
    source = replace(source, 0, substring(itob(array_length + new_items_count), 6, 8))
    source += new_items_bytes
    return source


@subroutine
def recalculate_array_offsets_dynamic(array_data: Bytes, start_at_index: UInt64) -> Bytes:
    """
    Recalculates the offset values of an arc4 dynamic array.

    array_data: The dynamic array data
    start_at_index: Optionally start at a non-zero index for performance optimisation. The offset
                    at this index is assumed to be correct if start_at_index is not 0

    returns: The updated bytes for the source array
    """
    return substring(array_data, 0, 2) + recalculate_array_offsets_static(
        extract(array_data, 2, 0),
        extract_uint16(array_data, 0),
        start_at_index,
    )


@subroutine
def recalculate_array_offsets_static(
    array_data: Bytes, length: UInt64, start_at_index: UInt64
) -> Bytes:
    """
    Recalculates the offset values of an arc4 static array.

    array_data: The static array data
    length: The length of the static array
    start_at_index: Optionally start at a non-zero index for performance optimisation. The offset
                    at this index is assumed to be correct if start_at_index is not 0

    returns: The updated bytes for the source array
    """
    header_cursor = start_at_index * 2
    if start_at_index == 0:
        tail_cursor = length * 2
    else:
        tail_cursor = extract_uint16(array_data, header_cursor)

    for i in urange(start_at_index, length):  # noqa: B007
        tail_cursor_bytes = substring(itob(tail_cursor), 6, 8)
        array_data = replace(array_data, header_cursor, tail_cursor_bytes)
        tail_cursor += extract_uint16(array_data, tail_cursor) + 2
        header_cursor += 2

    return array_data