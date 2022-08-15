# SPDX-License-Identifier: GPL-2.0-or-later

from .devicerow import DeviceRow
from .gi_composites import GtkTemplate

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk  # noqa


@GtkTemplate(ui="/org/freedesktop/Piper/ui/WelcomePerspective.ui")
class WelcomePerspective(Gtk.Box):
    """A perspective to present a list of devices for the user to pick one to
    configure."""

    __gtype_name__ = "WelcomePerspective"

    __gsignals__ = {
        "device-selected": (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
    }

    listbox = GtkTemplate.Child()
    _titlebar = GtkTemplate.Child()

    def __init__(self, *args, **kwargs):
        """Instantiates a new WelcomePerspective."""
        Gtk.Box.__init__(self, *args, **kwargs)
        self.init_template()
        self.listbox.set_sort_func(self._listbox_sort_func)
        self.listbox.set_header_func(self._listbox_header_func)

    def set_devices(self, devices):
        """Sets the devices to present to the user.

        @param devices The devices to present, as [ratbagd.RatbagdDevice]
        """
        self.listbox.foreach(Gtk.Widget.destroy)
        for device in devices:
            self.add_device(device)

    def add_device(self, device):
        """Add a device to the list.

        @param device The device to add, as ratbagd.RatbagdDevice
        """
        self.listbox.add(DeviceRow(device))

    def remove_device(self, device):
        """Remove a device from the list.

        @param device The device to remove, as ratbagd.RatbagdDevice
        """
        for child in self.listbox.get_children():
            if child._device is device:
                child.destroy()
                break

    @GObject.Property
    def name(self):
        """The name of this perspective."""
        return "welcome_perspective"

    @GObject.Property
    def titlebar(self):
        """The titlebar to this perspective."""
        return self._titlebar

    @GObject.Property
    def can_go_back(self):
        """Whether this perspective wants a back button to be displayed in case
        there is more than one connected device."""
        return False

    @GObject.Property
    def can_shutdown(self):
        """Whether this perspective can safely shutdown."""
        return True

    @GtkTemplate.Callback
    def _on_device_row_activated(self, listbox, row):
        self.emit("device-selected", row.device)

    def _listbox_sort_func(self, row1, row2):
        name1 = row1.device.name.casefold()
        name2 = row2.device.name.casefold()
        if name1 < name2:
            return -1
        elif name1 == name2:
            return 0
        return 1

    def _listbox_header_func(self, row, before):
        if before is not None:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            row.set_header(separator)
