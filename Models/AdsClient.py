from lognplot.client import LognplotTcpClient
import pyads
import time
import ctypes
import struct
import datetime
import re
from collections import namedtuple
from typing import Type, List


class AdsClient:
    VariableDescriptionEntry = namedtuple(
        "Entry", ["name", "typename", "comment", "datatype", "datatype_size"]
    )

    VariableDatatypeEntry = namedtuple(
        "Type", ["name", "typename", "size", "comment", "sub_items"]
    )

    DATATYPE_MAP = {
        "BOOL": pyads.PLCTYPE_BOOL,
        "BYTE": pyads.PLCTYPE_BYTE,
        "DINT": pyads.PLCTYPE_DINT,
        "DWORD": pyads.PLCTYPE_DWORD,
        "INT": pyads.PLCTYPE_INT,
        "LREAL": pyads.PLCTYPE_LREAL,
        "REAL": pyads.PLCTYPE_REAL,
        "SINT": pyads.PLCTYPE_SINT,
        "UDINT": pyads.PLCTYPE_UDINT,
        "UINT": pyads.PLCTYPE_UINT,
        "USINT": pyads.PLCTYPE_USINT,
        "WORD": pyads.PLCTYPE_WORD,
    }  # type: Dict[str, Type]

    def __init__(
        self, ams_net_id: str, ams_net_port: str, lnp=None, plc_ip_address=None
    ):
        self.notification_handles = []
        self.lnp_client = lnp

        try:
            print("Connecting to plc...")
            self.plc = pyads.Connection(ams_net_id, ams_net_port, plc_ip_address)
            self.plc.open()
        except pyads.ADSError as e:
            print("Ads Error: ", e)

    def __del__(self):
        for handle in self.notification_handles:
            self.plc.del_device_notification(*handle)

        if self.plc is not None:
            self.plc.close()

    def subscribe_by_name(self, name: str, plc_type):
        if not plc_type in self.DATATYPE_MAP:
            return

        plc_type_mapped = self.DATATYPE_MAP[plc_type]
        attr = pyads.NotificationAttrib(ctypes.sizeof(plc_type_mapped))
        handles = self.plc.add_device_notification(
            name, attr, self.callback(plc_type_mapped), pyads.ADSTRANS_SERVERCYCLE
        )
        self.notification_handles.append(handles)

    def subscribe(self, pattern: str):
        parsed_entries = self.get_ads_entries()

        for entry in parsed_entries:
            if re.match(pattern, entry.name) is not None:
                if entry.typename in self.DATATYPE_MAP:
                    self.subscribe_by_name(entry.name, entry.typename)

    def callback(self, plc_type):
        @self.plc.notification(plc_type)
        def decorated_callback(handle, name, timestamp, value):
            if self.lnp_client is not None:
                self.lnp_client.send_sample(
                    name, AdsClient.format_timestamp(timestamp), float(value),
                )

        return decorated_callback

    def get_ads_entries(self):
        # Get upload info
        nSymbols, nSymSize, _, nDatatypeSize, _, _ = self.plc.read(
            0xF00F, 0, ctypes.c_ulong * 6
        )

        entries = self.plc.read(
            pyads.constants.ADSIGRP_SYM_UPLOAD, 0, ctypes.c_ubyte * nSymSize
        )

        parsed_entries = AdsClient.unpack_entries(bytes(entries), nSymSize, nSymbols)

        data_types = self.plc.read(0xF00E, 0, ctypes.c_ubyte * nDatatypeSize)

        data_type_entries = AdsClient.unpack_datatype_entries(
            bytes(data_types), nDatatypeSize
        )

        sub_entries = []
        for e in parsed_entries:
            new_entries = AdsClient.get_sub_items(e, data_type_entries)
            if len(new_entries) > 0:
                sub_entries.extend(new_entries,)

        parsed_entries.extend(sub_entries)

        return parsed_entries

    @staticmethod
    def get_sub_items(entry: VariableDescriptionEntry, data_type_entries):
        new_entries = []
        if entry is None:
            return new_entries

        if len(entry) <= 0:
            return None

        if entry.typename in data_type_entries:
            typ = data_type_entries[entry.typename]
            if len(typ.sub_items) > 0:
                for s in typ.sub_items:
                    e = AdsClient.VariableDescriptionEntry(
                        entry.name + "." + s.name, s.typename, s.comment, -1, s.size
                    )
                    sub = AdsClient.get_sub_items(e, data_type_entries)
                    new_entries.append(e)
                    new_entries.extend(sub)

        return new_entries

    @staticmethod
    def format_timestamp(timestamp: datetime):
        return time.mktime(timestamp.timetuple()) + timestamp.microsecond / 1e6

    @staticmethod
    def unpack_entry(data: bytes, index: int) -> (int, VariableDescriptionEntry):
        fmt = "<6I3H"
        (
            entry_length,  # length of complete symbol entry
            _,  # indexGroup of symbol: input, output etc.
            _,  # index offset of symbol
            entry_data_type_size,  # size of symbol (in bytes, 0 = bit)
            entry_data_type,  # adsDataType of symbol
            _,  # flags
            name_len,  # length of symbol name (excl. \0)
            type_len,  # length of type name (excl. \0)
            comment_len,  # length of of comment (excl. \0)
        ) = struct.unpack_from(fmt, data, index)

        name_offset = index + struct.calcsize(fmt)
        name = data[name_offset : name_offset + name_len].decode("ascii")

        type_offset = name_offset + name_len + 1
        typ = data[type_offset : type_offset + type_len].decode("ascii")

        comment_offset = type_offset + type_len + 1
        comment = data[comment_offset : comment_offset + comment_len].decode("ascii")

        return (
            entry_length,
            AdsClient.VariableDescriptionEntry(
                name, typ, comment, entry_data_type, entry_data_type_size
            ),
        )

    @staticmethod
    def unpack_entries(
        entries_data: bytes, size: int, count: int
    ) -> List[VariableDescriptionEntry]:
        parsed_entries = []
        index = 0
        while index < size:
            entry_size, entry = AdsClient.unpack_entry(entries_data, index)
            index += entry_size
            parsed_entries.append(entry)

        assert len(parsed_entries) == count
        assert index == size
        return parsed_entries

    @staticmethod
    def unpack_datatype_entry(data: bytes, index: int) -> (int, VariableDatatypeEntry):
        fmt = "<8I5H"
        (
            entry_length,  # length of complete data type entry
            _,  # version of the data type structure
            _,  # hash value of data type to compare data types
            _,  # hash value of base type
            size,  # size of data type (in bytes)
            _,  # offs of data item in parent data type
            _,  # ads data type of symbol (if alias)
            _,  # flags
            name_len,  # length of data item  name (excl. \0)
            type_len,  # length of data item type name (excl. \0)
            comment_len,  # length of comment (excl. \0)
            array_dim,  #
            sub_items_count,  #
        ) = struct.unpack_from(fmt, data, index)

        name_offset = index + struct.calcsize(fmt)
        name = data[name_offset : name_offset + name_len].decode("ascii")

        type_offset = name_offset + name_len + 1
        typ = data[type_offset : type_offset + type_len].decode("ascii")

        comment_offset = type_offset + type_len + 1
        comment = data[comment_offset : comment_offset + comment_len].decode("ascii")

        fmt = "<" + str(array_dim) + "L"
        dim_offset = comment_offset + comment_len + 1
        dim = struct.unpack_from(fmt, data, dim_offset)

        sub_items_offset = dim_offset + struct.calcsize(fmt)
        sub_index = 0
        sub_items = []
        while sub_index < sub_items_count:
            sub_entry_size, sub_item = AdsClient.unpack_datatype_entry(
                data, sub_items_offset
            )
            sub_items_offset += sub_entry_size
            sub_index += 1
            sub_items.append(sub_item)

        return (
            entry_length,
            AdsClient.VariableDatatypeEntry(name, typ, size, comment, sub_items),
        )

    @staticmethod
    def unpack_datatype_entries(entries_data: bytes, size: int):
        parsed_entries = dict()
        index = 0
        while index < size:
            entry_size, entry = AdsClient.unpack_datatype_entry(entries_data, index)
            index += entry_size
            parsed_entries[entry.name] = entry

        assert index == size
        return parsed_entries
