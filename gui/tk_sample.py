#!/usr/bin/env python3
"""Minimal tkinter sample for libexword GUI mockup

Run with: python gui/tk_sample.py
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog

class LibexwordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('libexword GUI (tkinter mock)')
        self.geometry('900x520')

        self.language_var = tk.StringVar(value='ja')
        self._create_menu()
        self._create_widgets()
        self._populate_mock()

    def _create_widgets(self):
        # Paned window
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left: Own Devices
        left_frame = ttk.Frame(paned, width=260)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text='Own Devices').pack(anchor='nw')
        # Connected indicator
        self.connected_device = None
        self.connected_device_var = tk.StringVar(value='Connected: (none)')
        ttk.Label(left_frame, textvariable=self.connected_device_var).pack(anchor='nw', pady=(0,4))
        self.device_listbox = tk.Listbox(left_frame, height=20)
        self.device_listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.device_listbox.bind('<<ListboxSelect>>', self.on_device_select)
        # double-click to change active connection (asks for confirmation)
        self.device_listbox.bind('<Double-Button-1>', self.on_device_double_click)


        # Right: Files and buttons
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=4)
        # Device info (right top)
        self.device_info_var = tk.StringVar(value='Select a device')
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=4, pady=(0,6))
        ttk.Label(info_frame, text='Device Info').pack(anchor='w')
        tk.Label(info_frame, textvariable=self.device_info_var, relief=tk.SUNKEN, anchor='w', justify='left').pack(fill=tk.X, pady=2)
        # Files label
        ttk.Label(right_frame, text='Files').pack(anchor='nw')

        # Manager (left) <-> Device dictionaries (right)
        lists_frame = ttk.Frame(right_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Manager list
        manager_frame = ttk.Frame(lists_frame)
        manager_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(manager_frame, text='マネージャ内の追加辞書データ').pack(anchor='w')
        self.manager_listbox = tk.Listbox(manager_frame)
        manager_scroll = ttk.Scrollbar(manager_frame, orient=tk.VERTICAL, command=self.manager_listbox.yview)
        self.manager_listbox.config(yscrollcommand=manager_scroll.set)
        self.manager_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        manager_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Transfer buttons
        transfer_frame = ttk.Frame(lists_frame)
        transfer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(transfer_frame, text='→', width=3, command=self.on_add_to_device).pack(pady=6)
        ttk.Button(transfer_frame, text='←', width=3, command=self.on_remove_from_device).pack(pady=6)
        ttk.Button(transfer_frame, text='削除', width=6, command=self.on_manager_delete).pack(pady=6)

        # Device list (add-on dictionaries)
        device_files_frame = ttk.Frame(lists_frame)
        device_files_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(device_files_frame, text='電子辞書内の追加辞書データ').pack(anchor='w')
        self.device_files_listbox = tk.Listbox(device_files_frame)
        device_scroll = ttk.Scrollbar(device_files_frame, orient=tk.VERTICAL, command=self.device_files_listbox.yview)
        self.device_files_listbox.config(yscrollcommand=device_scroll.set)
        self.device_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        device_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Keep a reference to current device files for deletion/movements
        # (populated in on_device_select)
        # double-click to add; single-click should keep last device selected
        self.manager_listbox.bind('<Double-Button-1>', lambda e: self.on_add_to_device())
        self.manager_listbox.bind('<Button-1>', self._on_manager_click)
        self.device_files_listbox.bind('<Double-Button-1>', lambda e: self.on_remove_from_device())
        # ensure clicking device file selects it immediately so following actions work
        self.device_files_listbox.bind('<Button-1>', self._on_device_file_click)

        # Buttons (operations)
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, padx=4, pady=6)
        ttk.Button(btn_frame, text='Upload', command=self.on_upload).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Download', command=self.on_download).pack(side=tk.LEFT, padx=4)
        # Keep Delete as device file deletion (acts on selected device file)
        ttk.Button(btn_frame, text='Delete', command=self.on_delete_device_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Refresh', command=self.on_refresh).pack(side=tk.LEFT, padx=4)

        # Additional operations (right bottom)
        ops_frame = ttk.Frame(right_frame)
        ops_frame.pack(fill=tk.X, padx=4, pady=(4,8))
        ttk.Button(ops_frame, text='Install ZIP', command=self.on_install_zip).pack(side=tk.LEFT, padx=4)
        ttk.Button(ops_frame, text='File Explorer', command=self.on_file_explorer).pack(side=tk.LEFT, padx=4)
        ttk.Button(ops_frame, text='Link (Auth)', command=self.on_link_auth).pack(side=tk.LEFT, padx=4)

        # Status bar
        self.status = tk.StringVar(value='Ready')
        status_bar = ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _create_menu(self):
        # Menu bar
        menubar = tk.Menu(self)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Connect', command=self.on_connect)
        filemenu.add_command(label='Disconnect', command=self.on_disconnect)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.on_exit)
        menubar.add_cascade(label='File', menu=filemenu)
        # View menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label='Refresh', command=self.on_refresh)
        menubar.add_cascade(label='View', menu=viewmenu)
        # Settings menu (設定)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label='コマンドライン...', command=self.on_command_line)
        settings.add_command(label='設定...', command=self.on_preferences)
        # Language submenu
        langmenu = tk.Menu(settings, tearoff=0)
        langmenu.add_radiobutton(label='日本語 (Japanese)', variable=self.language_var, value='ja', command=lambda: self.on_set_language('ja'))
        langmenu.add_radiobutton(label='英語 (English)', variable=self.language_var, value='en', command=lambda: self.on_set_language('en'))
        langmenu.add_radiobutton(label='中国語 (Chinese)', variable=self.language_var, value='zh', command=lambda: self.on_set_language('zh'))
        settings.add_cascade(label='言語', menu=langmenu)
        settings.add_separator()
        settings.add_command(label='このソフトウェアについて', command=self.on_about)
        menubar.add_cascade(label='設定', menu=settings)
        # Dictionaries / Manager menu (辞書管理)
        dictmenu = tk.Menu(menubar, tearoff=0)
        dictmenu.add_command(label='追加 (From ZIP)...', command=self.on_add_from_zip)
        dictmenu.add_command(label='追加 (From folder)...', command=self.on_add_from_folder)
        dictmenu.add_command(label='追加 (From Github release)...', command=self.on_add_from_github)
        dictmenu.add_separator()
        dictmenu.add_command(label='マネージャの一覧を表示', command=self.on_show_manager_list)
        dictmenu.add_command(label='マネージャ内の辞書を削除', command=self.on_delete_from_manager)
        dictmenu.add_separator()
        dictmenu.add_command(label='認証情報をエクスポート...', command=self.on_export_auth)
        dictmenu.add_command(label='認証情報をインポート...', command=self.on_import_auth)
        dictmenu.add_command(label='選択デバイスの認証情報を再生成', command=self.on_regenerate_auth)
        menubar.add_cascade(label='辞書管理', menu=dictmenu)
        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='About', command=self.on_about)
        menubar.add_cascade(label='Help', menu=helpmenu)
        self.config(menu=menubar)


    def _populate_mock(self):
        # Mock device info mapping
        self.device_info_map = {
            'EX-word (USB0)': {
                'model': 'EX-100',
                'manufacturer': 'Casio',
                'product': 'EX-word 100',
                'files': [
                    ('example.txt', '1.2KB', '2026-01-01'),
                    ('manual.htm', '8KB', '2025-11-01'),
                ],
            },
            'EX-word (USB1)': {
                'model': 'EX-200',
                'manufacturer': 'Casio',
                'product': 'EX-word 200',
                'files': [
                    ('data.bmp', '12KB', '2025-12-10'),
                    ('readme.txt', '2KB', '2025-10-05'),
                ],
            },
        }

        # Devices
        for name in self.device_info_map.keys():
            self.device_listbox.insert(tk.END, name)
        self.device_listbox.selection_set(0)
        # remember last selected device (to avoid losing selection when clicking other widgets)
        self.last_selected_device = None

        # Manager DB (mock): list of dict entries (name, source)
        self.manager_db = [
            {'name': 'core_dict', 'source': 'builtin'},
            {'name': 'korean_pack', 'source': 'zip'},
        ]
        # Auth DB: device -> {username, key}
        self.auth_db = {
            # example: 'EX-word (USB0)': {'username': 'user1234', 'key': 'abcd...'}
        }

        # Trigger initial selection
        self.on_device_select(None)

    def on_upload(self):
        dev_name = self._require_connected()
        if not dev_name:
            return
        fname = filedialog.askopenfilename(title='Select file to upload')
        if fname:
            # Mock: add to device files
            import os, time
            name = os.path.basename(fname)
            self.device_info_map.setdefault(dev_name, {}).setdefault('files', []).append((name, f'{os.path.getsize(fname)//1024}KB', time.strftime('%Y-%m-%d')))
            self.on_device_select(None)
            self.status.set(f'Upload: {fname} to {dev_name}')
            print('Upload pressed:', fname)

    def on_download(self):
        dev_name = self._require_connected()
        if not dev_name:
            return
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo('Info', 'No file selected')
            return
        dest = filedialog.asksaveasfilename(initialfile=self.tree.item(sel)['values'][0])
        if dest:
            self.status.set(f'Download: {dest}')
            print('Download pressed:', dest)

    def on_delete(self):
        # legacy: kept for compatibility but acts on device file list
        self.on_delete_device_file()

    def on_refresh(self):
        self.status.set('Refreshed')
        print('Refresh pressed')

    def on_install_zip(self):
        # ensure device selection is restored if lost due to focus change
        self._restore_device_selection()
        dev_name = self._require_connected()
        if not dev_name:
            return
        path = filedialog.askopenfilename(title='Select ZIP to install', filetypes=[('Zip files', '*.zip')])
        if not path:
            return
        # Realistic install mock: extract zip to a temp folder and add entries for each file
        import os, zipfile, time
        try:
            with zipfile.ZipFile(path, 'r') as z:
                namelist = z.namelist()
                # add each top-level file as dict entry (mock behavior)
                for fn in namelist:
                    base = os.path.splitext(os.path.basename(fn))[0]
                    if base:
                        newfile = f'{base}.dict'
                        self.device_info_map[dev_name]['files'].append((newfile, '4KB', time.strftime('%Y-%m-%d')))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to install ZIP: {e}')
            return
        # ensure connection selection is shown
        try:
            idx = list(self.device_listbox.get(0, tk.END)).index(dev_name)
            self.device_listbox.selection_clear(0, tk.END)
            self.device_listbox.selection_set(idx)
        except ValueError:
            pass
        self.on_device_select(None)
        self.status.set(f'Installed ZIP: {os.path.basename(path)} to {dev_name}')
        print('Install ZIP:', path, 'to', dev_name)

    def on_file_explorer(self):
        # Show a dialog with files on the connected device (mock)
        dev_name = self._require_connected()
        if not dev_name:
            return
        # Build a simple mock filesystem view per device if not present
        fs = self.device_info_map.setdefault(dev_name, {}).setdefault('fs', None)
        files_flat = self.device_info_map.get(dev_name, {}).get('files', [])
        if fs is None:
            # initialize FS: root contains SD and mem directories and files in mem
            fs = {'/': ['SD <directory>', 'mem <directory>'],
                  '/SD': ['..', 'sd_dict.dict'],
                  '/mem': ['..'] + [f[0] for f in files_flat]}
            self.device_info_map[dev_name]['fs'] = fs
        current_path = ['/']  # use list for mutability in closure

        top = tk.Toplevel(self)
        top.title(f'File Explorer - {dev_name}')
        top.geometry('520x380')

        # Path/display frame with SD | mem buttons
        path_frame = ttk.Frame(top)
        path_frame.pack(fill=tk.X, padx=8, pady=6)
        path_label = ttk.Label(path_frame, text=f'Path: {current_path[0]}')
        path_label.pack(side=tk.LEFT)
        ttk.Button(path_frame, text='SD', command=lambda: _change_path('/SD')).pack(side=tk.RIGHT, padx=4)
        ttk.Button(path_frame, text='mem', command=lambda: _change_path('/mem')).pack(side=tk.RIGHT)

        lb = tk.Listbox(top)
        lb.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        def _refresh_list():
            lb.delete(0, tk.END)
            p = current_path[0]
            entries = fs.get(p, [])
            for e in entries:
                lb.insert(tk.END, e)
            path_label.config(text=f'Path: {p}')

        def _change_path(path):
            if path not in fs:
                messagebox.showinfo('Info', f'No such directory: {path}')
                return
            current_path[0] = path
            _refresh_list()

        # selection helpers
        def _select_under_mouse(event):
            try:
                idx = lb.nearest(event.y)
                bbox = lb.bbox(idx)
                if bbox:
                    lb.selection_clear(0, tk.END)
                    lb.selection_set(idx)
            except Exception:
                pass
        lb.bind('<Button-1>', _select_under_mouse)

        def ensure_selection():
            s = lb.curselection()
            if s:
                return True
            # try selecting under mouse pointer
            try:
                root_y = lb.winfo_rooty()
                mouse_y = self.winfo_pointery()
                rel_y = mouse_y - root_y
                if rel_y < 0 or rel_y > lb.winfo_height():
                    return False
                idx = lb.nearest(rel_y)
                lb.selection_clear(0, tk.END)
                lb.selection_set(idx)
                return True
            except Exception:
                return False

        def on_item_activate(event=None):
            # double-click or activate
            if not ensure_selection():
                messagebox.showinfo('Info', 'No file selected')
                return
            s = lb.curselection()
            item = lb.get(s[0])
            if item == '..':
                # go to parent
                if current_path[0] == '/':
                    return
                # simple parent logic: split last component
                if current_path[0].count('/') <= 1:
                    _change_path('/')
                else:
                    parent = '/'.join(current_path[0].rstrip('/').split('/')[:-1]) or '/'
                    _change_path(parent)
                return
            if item.endswith('<directory>'):
                # navigate into directory
                name = item.replace(' <directory>', '')
                newpath = ('/' + name) if not item.startswith('/') else name
                if newpath not in fs:
                    # create empty directory
                    fs[newpath] = ['..']
                _change_path(newpath)
                return
            # otherwise treat as file -> save-as
            # strip any tab-delimited extra info
            fname = item.split('\t')[0]
            dest = filedialog.asksaveasfilename(title='Save file as', initialfile=fname)
            if not dest:
                return
            messagebox.showinfo('Get', f"(Mock) Saved {fname} to {dest}")
            self.status.set(f'Saved {fname} to {dest}')

        lb.bind('<Double-Button-1>', on_item_activate)

        # Initial populate
        _refresh_list()

        btns = ttk.Frame(top)
        btns.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(btns, text='Open', command=lambda: messagebox.showinfo('Info', 'Open not implemented')).pack(side=tk.LEFT)
        ttk.Button(btns, text='Send', command=lambda: send_file()).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text='Delete', command=lambda: delete_file()).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text='Close', command=top.destroy).pack(side=tk.RIGHT)
        self.status.set(f'Opened explorer for {dev_name}')
        print('File Explorer open for:', dev_name)

    def on_link_auth(self):
        # Auto-generate auth info and store internally for connected device
        dev_name = self._require_connected()
        if not dev_name:
            return
        # generate username and 20-byte key (hex)
        import uuid, secrets
        username = f'user-{uuid.uuid4().hex[:8]}'
        key = secrets.token_hex(20)
        self.auth_db[dev_name] = {'username': username, 'key': key}
        self.on_device_select(None)
        self.status.set(f'Linked {dev_name} as {username}')
        print('Link(Auth) generated:', dev_name, username, key)

    def on_device_select(self, event):
        # Prefer connected device; fall back to selection or last_selected_device
        name = self.get_active_device()
        if not name:
            self.device_info_var.set('No device selected')
            # clear lists
            self.device_files_listbox.delete(0, tk.END)
            self.refresh_manager_listview()
            return
        # ensure the device is selected in the UI
        try:
            idx = list(self.device_listbox.get(0, tk.END)).index(name)
            self.device_listbox.selection_clear(0, tk.END)
            self.device_listbox.selection_set(idx)
        except ValueError:
            pass
        info = self.device_info_map.get(name, {})
        text = f"Model: {info.get('model','-')}\nManufacturer: {info.get('manufacturer','-')}\nProduct: {info.get('product','-')}"
        auth = self.auth_db.get(name)
        if auth:
            text += f"\nAuth: {auth.get('username')}"
        else:
            text += "\nAuth: (not linked)"
        self.device_info_var.set(text)
        # record last selected device
        self.last_selected_device = name
        # Update device files list
        self.device_files_listbox.delete(0, tk.END)
        for f in info.get('files', []):
            # consider only add-on dictionary files (mock: files ending with .dict)
            if f[0].endswith('.dict'):
                self.device_files_listbox.insert(tk.END, f[0])
        # refresh manager list
        self.refresh_manager_listview()

    def refresh_manager_listview(self):
        self.manager_listbox.delete(0, tk.END)
        for d in self.manager_db:
            self.manager_listbox.insert(tk.END, d['name'])

    def get_active_device(self):
        # Prefer the connected device; otherwise use currently selected device or last selected device
        if getattr(self, 'connected_device', None):
            return self.connected_device
        sel = self.device_listbox.curselection()
        if sel:
            return self.device_listbox.get(sel[0])
        if getattr(self, 'last_selected_device', None):
            return self.last_selected_device
        return None

    def _require_connected(self):
        """Return connected device name or show message and return None."""
        if not getattr(self, 'connected_device', None):
            messagebox.showinfo('Info', 'No device connected')
            return None
        return self.connected_device

    def on_add_to_device(self):
        # ensure device selection is restored if lost due to focus change
        self._restore_device_selection()
        # ensure manager selection (if click didn't commit selection yet) by checking mouse position
        if not self._ensure_manager_selected():
            messagebox.showinfo('Info', 'Select manager entry')
            return
        sel = self.manager_listbox.curselection()
        if not sel:
            messagebox.showinfo('Info', 'Select manager entry')
            return
        mgr_name = self.manager_listbox.get(sel[0])
        dev_name = self._require_connected()
        if not dev_name:
            return
        # move from manager to device as .dict
        import time
        self.device_info_map[dev_name]['files'].append((f'{mgr_name}.dict', '4KB', time.strftime('%Y-%m-%d')))
        # remove from manager_db
        self.manager_db = [m for m in self.manager_db if m['name'] != mgr_name]
        self.refresh_manager_listview()
        # ensure device selection is shown after action (highlight connected device)
        try:
            idx = list(self.device_listbox.get(0, tk.END)).index(dev_name)
            self.device_listbox.selection_clear(0, tk.END)
            self.device_listbox.selection_set(idx)
        except ValueError:
            pass
        self.on_device_select(None)
        self.status.set(f'Added {mgr_name} to {dev_name}')
        print('Add to device:', mgr_name, '->', dev_name)

    def _ensure_device_selected(self, event):
        # when manager list is clicked, preserve or restore last selected device
        # run after the click event to avoid interfering with listbox selection
        self.after(1, self._restore_device_selection)

    def _on_manager_click(self, event):
        """Select the manager list item under the mouse immediately on click.

        This ensures that clicking an item then immediately pressing the transfer
        button will have the manager entry selected even if selection wasn't
        committed by the time the button's command runs.
        """
        try:
            idx = self.manager_listbox.nearest(event.y)
            bbox = self.manager_listbox.bbox(idx)
            if bbox:
                # select that item
                self.manager_listbox.selection_clear(0, tk.END)
                self.manager_listbox.selection_set(idx)
        except Exception:
            pass
        # still preserve/restore device selection shortly after
        self.after(1, lambda: self._ensure_device_selected(event))

    def _restore_device_selection(self):
        # if device list has no selection but we had a last selected device, re-select it
        if not self.device_listbox.curselection() and getattr(self, 'last_selected_device', None):
            try:
                idx = list(self.device_listbox.get(0, tk.END)).index(self.last_selected_device)
                self.device_listbox.selection_clear(0, tk.END)
                self.device_listbox.selection_set(idx)
            except ValueError:
                # device not found
                pass

    def _ensure_manager_selected(self):
        # If manager list has a selection, OK
        if self.manager_listbox.curselection():
            return True
        # Try to select item under mouse pointer
        try:
            root_y = self.manager_listbox.winfo_rooty()
            mouse_y = self.winfo_pointery()
            rel_y = mouse_y - root_y
            if rel_y < 0 or rel_y > self.manager_listbox.winfo_height():
                return False
            idx = self.manager_listbox.nearest(rel_y)
            # select it
            self.manager_listbox.selection_clear(0, tk.END)
            self.manager_listbox.selection_set(idx)
            return True
        except Exception:
            return False

    def _ensure_device_file_selected(self):
        # If a device file is selected, OK
        if self.device_files_listbox.curselection():
            return True
        # Try to select item under mouse pointer
        try:
            root_y = self.device_files_listbox.winfo_rooty()
            mouse_y = self.winfo_pointery()
            rel_y = mouse_y - root_y
            if rel_y < 0 or rel_y > self.device_files_listbox.winfo_height():
                return False
            idx = self.device_files_listbox.nearest(rel_y)
            self.device_files_listbox.selection_clear(0, tk.END)
            self.device_files_listbox.selection_set(idx)
            return True
        except Exception:
            return False

    def _on_device_file_click(self, event):
        """Select the device file item under the mouse immediately on click.

        Ensures that clicking then immediately pressing the remove/other buttons
        will have the file entry selected even if selection wasn't committed.
        """
        try:
            idx = self.device_files_listbox.nearest(event.y)
            bbox = self.device_files_listbox.bbox(idx)
            if bbox:
                self.device_files_listbox.selection_clear(0, tk.END)
                self.device_files_listbox.selection_set(idx)
        except Exception:
            pass
        # also preserve/restore device selection shortly after
        self.after(1, lambda: self._ensure_device_selected(event))


    def on_remove_from_device(self):
        # ensure device selection is restored if lost due to focus change
        self._restore_device_selection()
        # ensure a device file is selected (try to select under mouse if needed)
        if not self._ensure_device_file_selected():
            messagebox.showinfo('Info', 'Select device file')
            return
        dsel = self.device_files_listbox.curselection()
        if not dsel:
            messagebox.showinfo('Info', 'Select device file')
            return
        dev_name = self._require_connected()
        if not dev_name:
            return
        fname = self.device_files_listbox.get(dsel[0])
        # remove from device files, and re-add to manager
        before = len(self.device_info_map[dev_name]['files'])
        self.device_info_map[dev_name]['files'] = [f for f in self.device_info_map[dev_name]['files'] if f[0] != fname]
        if before == len(self.device_info_map[dev_name]['files']):
            messagebox.showinfo('Info', 'Selected file not found on device')
            return
        name = fname[:-5] if fname.endswith('.dict') else fname
        self.manager_db.append({'name': name, 'source': 'device'})
        self.refresh_manager_listview()
        self.on_device_select(None)
        self.status.set(f'Removed {fname} from {dev_name} (moved to manager)')
        print('Remove from device:', fname, '-> manager')

    def on_manager_delete(self):
        # try to ensure manager selection under mouse if missing
        if not self._ensure_manager_selected():
            messagebox.showinfo('Info', 'No manager entry selected')
            return
        sel = self.manager_listbox.curselection()
        if not sel:
            messagebox.showinfo('Info', 'No manager entry selected')
            return
        name = self.manager_listbox.get(sel[0])
        if messagebox.askyesno('Confirm', f'Delete {name} from manager?'):
            self.manager_db = [m for m in self.manager_db if m['name'] != name]
            self.refresh_manager_listview()
            self.status.set(f'Deleted {name} from manager')
            print('Manager delete:', name)

    # --- Auth import/export/regenerate ---
    def on_export_auth(self):
        if not self.auth_db:
            messagebox.showinfo('Export', 'No auth data to export')
            return
        path = filedialog.asksaveasfilename(title='Export auth to file', defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        import json
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.auth_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export auth: {e}')
            return
        self.status.set(f'Auth exported to {path}')
        print('Auth exported:', path)

    def on_import_auth(self):
        path = filedialog.askopenfilename(title='Import auth from file', filetypes=[('JSON','*.json')])
        if not path:
            return
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Basic validation: expect dict of device:{username,key}
            for k, v in data.items():
                if isinstance(v, dict) and 'username' in v and 'key' in v:
                    self.auth_db[k] = v
            self.on_device_select(None)
            self.status.set(f'Auth imported from {path}')
            print('Auth imported:', path)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to import auth: {e}')

    def on_regenerate_auth(self):
        sel = self.device_listbox.curselection()
        if not sel:
            messagebox.showinfo('Info', 'Select a device to regenerate auth')
            return
        dev_name = self.device_listbox.get(sel[0])
        import uuid, secrets
        username = f'user-{uuid.uuid4().hex[:8]}'
        key = secrets.token_hex(20)
        self.auth_db[dev_name] = {'username': username, 'key': key}
        self.on_device_select(None)
        self.status.set(f'Regenerated auth for {dev_name}')
        print('Regenerated auth for:', dev_name, username, key)

    def on_delete_device_file(self):
        dev_name = self._require_connected()
        if not dev_name:
            return
        dsel = self.device_files_listbox.curselection()
        if not dsel:
            messagebox.showinfo('Info', 'Select device file')
            return
        fname = self.device_files_listbox.get(dsel[0])
        if messagebox.askyesno('Confirm', f'Delete {fname} from {dev_name}?'):
            self.device_info_map[dev_name]['files'] = [f for f in self.device_info_map[dev_name]['files'] if f[0] != fname]
            self.on_device_select(None)
            self.status.set(f'Deleted {fname} from {dev_name}')
            print('Deleted device file:', fname)

    def on_connect(self):
        # Connect to currently selected device (or last selected)
        sel = self.device_listbox.curselection()
        dev = None
        if sel:
            dev = self.device_listbox.get(sel[0])
        elif getattr(self, 'last_selected_device', None):
            dev = self.last_selected_device
        if not dev:
            messagebox.showinfo('Info', 'No device selected')
            return
        # confirm
        if not messagebox.askyesno('Connect', f'接続を {dev} に変更しますか？'):
            return
        self._change_connection(dev)

    def on_disconnect(self):
        if not self.connected_device:
            messagebox.showinfo('Info', 'No active connection')
            return
        if not messagebox.askyesno('Disconnect', f'{self.connected_device} から切断しますか？'):
            return
        self._change_connection(None)

    def _change_connection(self, dev_name):
        # dev_name == None => disconnect
        if dev_name is None:
            self.connected_device = None
            self.connected_device_var.set('Connected: (none)')
            self.status.set('Disconnected')
            print('Disconnected')
            # update device info display
            self.on_device_select(None)
            return
        # connect
        self.connected_device = dev_name
        self.connected_device_var.set(f'Connected: {dev_name}')
        self.status.set(f'Connected to {dev_name}')
        # ensure device is selected in list
        try:
            idx = list(self.device_listbox.get(0, tk.END)).index(dev_name)
            self.device_listbox.selection_clear(0, tk.END)
            self.device_listbox.selection_set(idx)
        except ValueError:
            pass
        print('Connected to', dev_name)
        # update device info display
        self.on_device_select(None)

    def on_device_double_click(self, event):
        sel = self.device_listbox.curselection()
        if not sel:
            return
        name = self.device_listbox.get(sel[0])
        # confirm change
        if name == self.connected_device:
            messagebox.showinfo('Info', f'{name} は既に接続済みです')
            return
        if messagebox.askyesno('接続の変更', '接続を変更しますか？'):
            self._change_connection(name)

    def on_exit(self):
        self.destroy()

    def on_about(self):
        messagebox.showinfo('About', 'libexword GUI mock\nTkinter sample')

    def on_command_line(self):
        from tkinter import simpledialog
        cmd = simpledialog.askstring('Command Line', 'Enter command line options (mock):')
        if cmd is None:
            return
        messagebox.showinfo('Command Line', f'Set command line: {cmd}')
        self.status.set('Command line set')

    def on_preferences(self):
        messagebox.showinfo('Settings', 'Preferences dialog (mock)')
        self.status.set('Opened preferences')

    def on_set_language(self, lang):
        names = {'ja':'日本語', 'en':'English', 'zh':'中文'}
        self.language_var.set(lang)
        self.status.set(f'Language set: {names.get(lang, lang)}')
        messagebox.showinfo('Language', f"Set language to {names.get(lang, lang)}")

    # --- Dictionary management actions (mock implementations) ---
    def on_add_from_zip(self):
        path = filedialog.askopenfilename(title='Select ZIP', filetypes=[('Zip files','*.zip')])
        if not path:
            return
        import os
        name = os.path.splitext(os.path.basename(path))[0]
        self.manager_db.append({'name': name, 'source': 'zip'})
        self.status.set(f'Added {name} from ZIP')
        print('Add from ZIP:', path)

    def on_add_from_folder(self):
        path = filedialog.askdirectory(title='Select folder to add')
        if not path:
            return
        import os
        name = os.path.basename(path.rstrip('/\\'))
        self.manager_db.append({'name': name, 'source': 'folder'})
        self.status.set(f'Added {name} from folder')
        print('Add from folder:', path)

    def on_add_from_github(self):
        # Simple prompt for GitHub release URL (mock)
        from tkinter import simpledialog
        url = simpledialog.askstring('GitHub', 'Enter GitHub release URL')
        if not url:
            return
        name = url.split('/')[-1] if '/' in url else url
        self.manager_db.append({'name': name, 'source': 'github'})
        self.status.set(f'Added {name} from GitHub')
        print('Add from GitHub:', url)

    def on_show_manager_list(self):
        if not self.manager_db:
            messagebox.showinfo('Manager', 'No dictionaries in manager')
            return
        text = '\n'.join([f"{d['name']} ({d['source']})" for d in self.manager_db])
        messagebox.showinfo('Manager List', text)

    def on_delete_from_manager(self):
        from tkinter import simpledialog
        name = simpledialog.askstring('Delete', 'Enter dictionary name to delete')
        if not name:
            return
        before = len(self.manager_db)
        self.manager_db = [d for d in self.manager_db if d['name'] != name]
        after = len(self.manager_db)
        if before == after:
            messagebox.showinfo('Delete', f'No entry named {name} found')
        else:
            messagebox.showinfo('Delete', f'Deleted {name}')
            self.status.set(f'Deleted {name}')


if __name__ == '__main__':
    app = LibexwordApp()
    app.mainloop()
