# Copyright (C) 2024-2025 Analog Devices, Inc.
#
# SPDX short identifier: ADIBSD


from decimal import Decimal

import numpy as np

from adi.attribute import attribute
from adi.context_manager import context_manager
from adi.rx_tx import rx


class ad4170(rx, context_manager):
    """ AD4170 ADC """

    _complex_data = False
    channels = []  # type: ignore
    _device_name = ""

    def __init__(self, uri="", device_name=""):

        context_manager.__init__(self, uri, self._device_name)

        compatible_parts = ["ad4170", "ad4190"]

        self._ctrl = None

        if not device_name:
            device_name = compatible_parts[0]
        else:
            if device_name not in compatible_parts:
                raise Exception("Not a compatible device: " + device_name)

        # Select the device matching device_name as working device
        for device in self._ctx.devices:
            if device.name == device_name:
                self._ctrl = device
                self._rxadc = device
                break

        self.channels = []
        for ch in self._ctrl.channels:
            name = ch._id
            self._rx_channel_names.append(name)
            self.channels.append(self._channel(self._ctrl, name))

        rx.__init__(self)

    class _channel(attribute):
        """AD4170 channel"""

        def __init__(self, ctrl, channel_name):
            self.name = channel_name
            self._ctrl = ctrl

        @property
        def raw(self):
            """AD4170 channel raw value"""
            return self._get_iio_attr(self.name, "raw", False)

        @property
        def offset(self):
            """AD4170 channel offset"""
            return float(self._get_iio_attr_str(self.name, "offset", False))

        @offset.setter
        def offset(self, value):
            self._set_iio_attr(self.name, "offset", False, str(Decimal(value).real))

        @property
        def scale(self):
            """AD4170 channel scale"""
            return float(self._get_iio_attr_str(self.name, "scale", False))

        @scale.setter
        def scale(self, value):
            self._set_iio_attr(self.name, "scale", False, str(Decimal(value).real))

    def to_volts(self, index, val):
        """Converts raw value to SI
            index - Channel index
            val- Raw value """
        _scale = self.channel[index].scale

        ret = None

        if isinstance(val, np.int16):
            ret = val * _scale

        if isinstance(val, np.ndarray):
            ret = [x * _scale for x in val]

        return ret
