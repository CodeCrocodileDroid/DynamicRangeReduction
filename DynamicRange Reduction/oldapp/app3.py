import wx
import os
import sys

def reduce_color_depth(image, bits=4):
    """
    Reduce the color depth of the image by quantizing each RGB channel.
    bits: number of bits per channel (e.g., 4 => 16 levels per channel)
    Returns a new wx.Image with reduced color depth.
    """
    if bits < 1 or bits > 8:
        raise ValueError("Bits must be between 1 and 8")
    levels = 2 ** bits
    scale = 256 // levels

    width = image.GetWidth()
    height = image.GetHeight()
    data = image.GetData()
    if isinstance(data, bytes):
        data = bytearray(data)
    else:
        data = bytearray(data)

    for i in range(0, len(data), 3):
        r = data[i]
        g = data[i+1]
        b = data[i+2]
        # Quantize each channel
        r = (r // scale) * scale
        g = (g // scale) * scale
        b = (b // scale) * scale
        data[i] = r
        data[i+1] = g
        data[i+2] = b

    new_image = wx.Image(width, height)
    new_image.SetData(bytes(data))
    if image.HasAlpha():
        new_image.SetAlpha(image.GetAlpha())
    return new_image

class UniversalImageViewer(wx.Frame):
    def __init__(self, parent, title):
        super(UniversalImageViewer, self).__init__(parent, title=title, size=(900, 700))
        self.current_image = None
        self.image_path = None
        self.original_image = None
        self.supported_formats = self.get_supported_formats()
        self.init_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.Centre()
        self.Show()

    def get_supported_formats(self):
        """Get supported formats with safe constant handling"""
        formats = {
            '.bmp': wx.BITMAP_TYPE_BMP,
            '.bitmap': wx.BITMAP_TYPE_BMP,
            '.jpg': wx.BITMAP_TYPE_JPEG,
            '.jpeg': wx.BITMAP_TYPE_JPEG,
            '.jpe': wx.BITMAP_TYPE_JPEG,
            '.jfif': wx.BITMAP_TYPE_JPEG,
            '.png': wx.BITMAP_TYPE_PNG,
            '.gif': wx.BITMAP_TYPE_GIF,
            '.tif': wx.BITMAP_TYPE_TIF,
            '.tiff': wx.BITMAP_TYPE_TIF,
            '.pcx': wx.BITMAP_TYPE_PCX,
            '.ico': wx.BITMAP_TYPE_ICO,
            '.icon': wx.BITMAP_TYPE_ICO,
            '.cur': wx.BITMAP_TYPE_CUR,
            '.ani': wx.BITMAP_TYPE_ANI,
            '.pnm': wx.BITMAP_TYPE_PNM,
            '.pbm': wx.BITMAP_TYPE_PNM,
            '.pgm': wx.BITMAP_TYPE_PNM,
            '.ppm': wx.BITMAP_TYPE_PNM,
            '.xpm': wx.BITMAP_TYPE_XPM,
        }
        conditional_formats = {
            'BITMAP_TYPE_WEBP': ('.webp', 'WEBP format'),
            'BITMAP_TYPE_ICNS': ('.icns', 'Apple Icon format'),
            'BITMAP_TYPE_TGA': ('.tga', 'Targa format'),
        }
        for const_name, (extension, description) in conditional_formats.items():
            if hasattr(wx, const_name):
                formats[extension] = getattr(wx, const_name)
                print(f"Added support for {description} ({extension})")
            else:
                print(f"Note: {description} ({extension}) not available in this wxPython version")
        return formats

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window = wx.ScrolledWindow(panel)
        self.scrolled_window.SetScrollRate(10, 10)
        self.scrolled_window.SetMinSize((700, 500))
        self.image_ctrl = wx.StaticBitmap(self.scrolled_window)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.image_ctrl, 1, wx.EXPAND)
        self.scrolled_window.SetSizer(scroll_sizer)
        info_panel = wx.Panel(panel)
        info_sizer = wx.GridBagSizer(5, 5)
        self.file_label = wx.StaticText(info_panel, label="File: None")
        self.size_label = wx.StaticText(info_panel, label="Size: N/A")
        self.format_label = wx.StaticText(info_panel, label="Format: N/A")
        self.dimensions_label = wx.StaticText(info_panel, label="Dimensions: N/A")
        info_sizer.Add(self.file_label, pos=(0, 0), flag=wx.EXPAND)
        info_sizer.Add(self.size_label, pos=(0, 1), flag=wx.EXPAND)
        info_sizer.Add(self.format_label, pos=(1, 0), flag=wx.EXPAND)
        info_sizer.Add(self.dimensions_label, pos=(1, 1), flag=wx.EXPAND)
        info_panel.SetSizer(info_sizer)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(info_panel, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(main_sizer)

    def create_menu(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, "&Open Image\tCtrl+O", "Open an image file")
        open_folder_item = file_menu.Append(wx.ID_ANY, "Open &Folder\tCtrl+F", "Open all images from a folder")
        file_menu.AppendSeparator()
        self.save_item = file_menu.Append(wx.ID_SAVE, "&Save Image\tCtrl+S", "Save current image")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit application")

        view_menu = wx.Menu()
        self.fit_item = view_menu.AppendRadioItem(wx.ID_ANY, "&Fit to Window", "Fit image to window")
        self.actual_size_item = view_menu.AppendRadioItem(wx.ID_ANY, "&Actual Size", "Show image at actual size")
        view_menu.Check(self.fit_item.GetId(), True)
        view_menu.AppendSeparator()
        zoom_in_item = view_menu.Append(wx.ID_ZOOM_IN, "Zoom &In\tCtrl++", "Zoom in")
        zoom_out_item = view_menu.Append(wx.ID_ZOOM_OUT, "Zoom &Out\tCtrl+-", "Zoom out")
        zoom_reset_item = view_menu.Append(wx.ID_ZOOM_100, "&Reset Zoom\tCtrl+0", "Reset zoom to 100%")

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        formats_item = help_menu.Append(wx.ID_ANY, "Supported &Formats", "Show supported formats")

        menubar.Append(file_menu, "&File")
        menubar.Append(view_menu, "&View")
        menubar.Append(help_menu, "&Help")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_open_folder, open_folder_item)
        self.Bind(wx.EVT_MENU, self.on_save, self.save_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_fit_to_window, self.fit_item)
        self.Bind(wx.EVT_MENU, self.on_actual_size, self.actual_size_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_in, zoom_in_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_out, zoom_out_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_reset, zoom_reset_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_show_formats, formats_item)

    def create_toolbar(self):
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_TEXT)
        open_tool = toolbar.AddTool(wx.ID_OPEN, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        save_tool = toolbar.AddTool(wx.ID_SAVE, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        toolbar.AddSeparator()
        reduce_tool = toolbar.AddTool(wx.ID_ANY, "Reduce Colors", wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE))
        toolbar.AddSeparator()
        zoom_in_tool = toolbar.AddTool(wx.ID_ZOOM_IN, "Zoom In", wx.ArtProvider.GetBitmap(wx.ART_PLUS))
        zoom_out_tool = toolbar.AddTool(wx.ID_ZOOM_OUT, "Zoom Out", wx.ArtProvider.GetBitmap(wx.ART_MINUS))
        zoom_reset_tool = toolbar.AddTool(wx.ID_ZOOM_100, "Actual Size", wx.ArtProvider.GetBitmap(wx.ART_GO_HOME))
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.on_open, open_tool)
        self.Bind(wx.EVT_TOOL, self.on_save, save_tool)
        self.Bind(wx.EVT_TOOL, self.on_reduce_colors, reduce_tool)
        self.Bind(wx.EVT_TOOL, self.on_zoom_in, zoom_in_tool)
        self.Bind(wx.EVT_TOOL, self.on_zoom_out, zoom_out_tool)
        self.Bind(wx.EVT_TOOL, self.on_zoom_reset, zoom_reset_tool)

    def create_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Ready - Open an image to begin")

    def get_supported_wildcards(self):
        extensions = {}
        for ext, bmp_type in self.supported_formats.items():
            if ext in ['.jpg', '.jpeg', '.jpe', '.jfif']:
                extensions.setdefault('JPEG', []).append(ext[1:])
            elif ext in ['.tif', '.tiff']:
                extensions.setdefault('TIFF', []).append(ext[1:])
            elif ext in ['.pnm', '.pbm', '.pgm', '.ppm']:
                extensions.setdefault('PNM', []).append(ext[1:])
            else:
                format_name = ext[1:].upper()
                extensions.setdefault(format_name, []).append(ext[1:])
        wildcards = []
        all_extensions = []
        for format_name, ext_list in extensions.items():
            ext_pattern = ';'.join([f'*.{ext}' for ext in ext_list])
            wildcards.append(f"{format_name} files ({ext_pattern})|{ext_pattern}")
            all_extensions.extend([f'*.{ext}' for ext in ext_list])
        all_supported = ";".join(all_extensions)
        wildcards.insert(0, f"All supported images ({all_supported})|{all_supported}")
        wildcards.append("All files (*.*)|*.*")
        return "|".join(wildcards)

    def on_open(self, event):
        wildcard = self.get_supported_wildcards()
        with wx.FileDialog(self, "Open Image file", wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.image_path = file_dialog.GetPath()
            self.load_image(self.image_path)

    def on_open_folder(self, event):
        with wx.DirDialog(self, "Choose a folder containing images") as dir_dialog:
            if dir_dialog.ShowModal() == wx.ID_CANCEL:
                return
            folder_path = dir_dialog.GetPath()
            self.load_images_from_folder(folder_path)

    def load_images_from_folder(self, folder_path):
        supported_files = []
        for filename in os.listdir(folder_path):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in self.supported_formats:
                supported_files.append(os.path.join(folder_path, filename))
        if supported_files:
            self.image_path = supported_files[0]
            self.load_image(self.image_path)
            self.statusbar.SetStatusText(f"Loaded 1 of {len(supported_files)} images from folder")
        else:
            wx.MessageBox("No supported image files found in the selected folder.", "Info", wx.OK | wx.ICON_INFORMATION)

    def load_image(self, path):
        try:
            file_ext = os.path.splitext(path)[1].lower()
            if file_ext in self.supported_formats:
                bitmap_type = self.supported_formats[file_ext]
                image = wx.Image(path, bitmap_type)
            else:
                image = wx.Image(path, wx.BITMAP_TYPE_ANY)
            if not image.IsOk():
                image = wx.Image(path, wx.BITMAP_TYPE_ANY)
                if not image.IsOk():
                    wx.MessageBox(
                        "Failed to load image! The file might be corrupted or in an unsupported format.",
                        "Error", wx.OK | wx.ICON_ERROR
                    )
                    return
            self.original_image = image
            self.current_image = image
            self.display_image()
            filename = os.path.basename(path)
            file_size = os.path.getsize(path)
            dimensions = f"{image.GetWidth()} × {image.GetHeight()}"
            file_size_str = self.format_file_size(file_size)
            self.file_label.SetLabel(f"File: {filename}")
            self.size_label.SetLabel(f"Size: {file_size_str}")
            self.format_label.SetLabel(f"Format: {file_ext.upper() or 'Unknown'}")
            self.dimensions_label.SetLabel(f"Dimensions: {dimensions}")
            self.statusbar.SetStatusText(f"Loaded: {filename} - {dimensions}")
        except Exception as e:
            wx.MessageBox(f"Error loading image: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def display_image(self):
        if self.current_image is None:
            return
        image = self.current_image
        if self.fit_item.IsChecked():
            display_size = self.scrolled_window.GetClientSize()
            img_width = image.GetWidth()
            img_height = image.GetHeight()
            if img_width > 0 and img_height > 0:
                scale_x = display_size.width / img_width
                scale_y = display_size.height / img_height
                scale = min(scale_x, scale_y)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        self.image_ctrl.SetBitmap(bitmap)
        self.scrolled_window.SetVirtualSize(bitmap.GetSize())
        self.scrolled_window.Layout()
        self.Layout()

    def on_fit_to_window(self, event):
        self.display_image()

    def on_actual_size(self, event):
        if self.original_image:
            self.current_image = self.original_image
            self.display_image()

    def on_zoom_in(self, event):
        if self.original_image and self.actual_size_item.IsChecked():
            width = int(self.current_image.GetWidth() * 1.2)
            height = int(self.current_image.GetHeight() * 1.2)
            self.current_image = self.original_image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
            self.display_image()

    def on_zoom_out(self, event):
        if self.original_image and self.actual_size_item.IsChecked():
            width = int(self.current_image.GetWidth() * 0.8)
            height = int(self.current_image.GetHeight() * 0.8)
            self.current_image = self.original_image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
            self.display_image()

    def on_zoom_reset(self, event):
        self.on_actual_size(event)

    def on_reduce_colors(self, event):
        if self.current_image is None:
            wx.MessageBox("No image loaded!", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        # Apply 4-bit per channel reduction (16 levels per channel)
        try:
            reduced_image = reduce_color_depth(self.current_image, bits=4)
            self.current_image = reduced_image
            self.display_image()
            self.statusbar.SetStatusText("Color depth reduced to 4 bits per channel.")
        except Exception as e:
            wx.MessageBox(f"Error reducing colors: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def on_save(self, event):
        if self.current_image is None:
            wx.MessageBox("No image to save!", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        wildcard = self.get_supported_wildcards()
        with wx.FileDialog(self, "Save Image", wildcard=wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            output_path = file_dialog.GetPath()
            file_ext = os.path.splitext(output_path)[1].lower()
            if file_ext not in self.supported_formats:
                wx.MessageBox("Unsupported file format for saving.", "Error", wx.OK | wx.ICON_ERROR)
                return
            bitmap_type = self.supported_formats[file_ext]
            if not self.current_image.SaveFile(output_path, bitmap_type):
                wx.MessageBox("Failed to save image!", "Error", wx.OK | wx.ICON_ERROR)
            else:
                self.statusbar.SetStatusText(f"Image saved to {output_path}")

    def on_about(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "Universal Image Viewer"
        info.Version = "1.1"
        info.Description = "Image viewer with dynamic range reduction and save support."
        info.Copyright = "(C) 2025"
        info.Developers = ["wxPython Image Viewer"]
        wx.AboutBox(info)

    def on_show_formats(self, event):
        formats_list = "\n".join([f"• {ext.upper()}" for ext in sorted(self.supported_formats.keys())])
        message = f"Supported Image Formats:\n{formats_list}\nTotal: {len(self.supported_formats)} formats"
        wx.MessageBox(message, "Supported Formats", wx.OK | wx.ICON_INFORMATION)

    def on_exit(self, event):
        self.Close()

class UniversalImageViewerApp(wx.App):
    def OnInit(self):
        print(f"wxPython version: {wx.VERSION_STRING}")
        frame = UniversalImageViewer(None, "Universal Image Viewer")
        frame.Show()
        return True

if __name__ == "__main__":
    app = UniversalImageViewerApp(False)
    app.MainLoop()