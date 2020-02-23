from lognplot.client import LognplotTcpClient
import pyads
import time
import ctypes
import struct
import datetime
import re
from collections import namedtuple
from typing import Type


class AdsClient:
    VariableDescriptionEntry = namedtuple(
        "Entry", ["name", "typename", "comment", "datatype", "datatype_size"]
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

    def __init__(self, ams_net_id: str, ams_net_port: str, lnp=None):
        self.notification_handles = []
        self.plc = pyads.Connection(ams_net_id, ams_net_port)
        self.lnp_client = lnp
        self.plc.open()

    def __del__(self):
        for handle in self.notification_handles:
            self.plc.del_device_notification(*handle)

        self.plc.close()

    def subscribe_by_name(self, name: str, plc_type):
        plc_type_mapped = self.DATATYPE_MAP[plc_type]
        attr = pyads.NotificationAttrib(ctypes.sizeof(plc_type_mapped))
        handles = self.plc.add_device_notification(
            name, attr, self.callback(plc_type), pyads.ADSTRANS_SERVERCYCLE
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
        upload_info = self._get_upload_info()
        entries = self.plc.read(
            pyads.constants.ADSIGRP_SYM_UPLOAD, 0, ctypes.c_ubyte * upload_info.nSymSize
        )

        parsed_entries = AdsClient.unpack_entries(
            bytes(entries), upload_info.nSymSize, upload_info.nSymbols
        )
        return parsed_entries

    def _get_upload_info(self):
        upload_info = self.plc.read(
            pyads.constants.ADSIGRP_SYM_UPLOADINFO,
            0,
            pyads.structs.SAdsSymbolUploadInfo,
        )
        return upload_info

    @staticmethod
    def format_timestamp(timestamp: datetime):
        return time.mktime(timestamp.timetuple()) + timestamp.microsecond / 1e6

    @staticmethod
    def unpack_entry(data: bytes, index: int) -> (int, VariableDescriptionEntry):
        fmt = "<6I3H"
        (
            entry_length,
            _,
            _,
            entry_datatype_size,
            entry_datatype,
            _,
            name_len,
            type_len,
            comment_len,
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
                name, typ, comment, entry_datatype, entry_datatype_size
            ),
        )

    @staticmethod
    def unpack_entries(entries_data: bytes, size: int, count: int):
        parsed_entries = []
        index = 0
        while index < size:
            entry_size, entry = AdsClient.unpack_entry(entries_data, index)
            index += entry_size
            parsed_entries.append(entry)

        assert len(parsed_entries) == count
        assert index == size
        return parsed_entries
