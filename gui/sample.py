#!/usr/bin/env python3
# Minimal PyGObject sample to load the Glade UI
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainApp:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file('gui/libexword_gui.ui')
        self.window = builder.get_object('main_window')
        self.device_list = builder.get_object('device_list')
        self.file_list = builder.get_object('file_list')
        builder.connect_signals(self)

        self.window.connect('destroy', Gtk.main_quit)

        # populate mock device and file list
        self._populate_mock()
        self.window.show_all()

    def _populate_mock(self):
        # device model: one column
        store = Gtk.ListStore(str)
        store.append(['EX-word (USB0)'])
        store.append(['EX-word (USB1)'])
        self.device_list.set_model(store)
        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('Devices', renderer, text=0)
        self.device_list.append_column(col)

        # file list: name,size,date
        fstore = Gtk.ListStore(str, str, str)
        fstore.append(['example.txt', '1.2KB', '2026-01-01'])
        fstore.append(['data.bmp', '12KB', '2025-12-10'])
        self.file_list.set_model(fstore)
        for i, title in enumerate(['Name', 'Size', 'Date']):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            self.file_list.append_column(col)

    def on_upload_button_clicked(self, button):
        print('Upload pressed')

    def on_download_button_clicked(self, button):
        print('Download pressed')

    def on_delete_button_clicked(self, button):
        print('Delete pressed')

    def on_refresh_button_clicked(self, button):
        print('Refresh pressed')

if __name__ == '__main__':
    app = MainApp()
    Gtk.main()
