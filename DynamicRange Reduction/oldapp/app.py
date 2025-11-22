import wx
import os


class SimpleImageViewer(wx.Frame):
    def __init__(self):
        super(SimpleImageViewer, self).__init__(None, title="Simple Image Viewer", size=(600, 500))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create open button
        self.open_btn = wx.Button(panel, label="Open Image")
        self.open_btn.Bind(wx.EVT_BUTTON, self.on_open)

        # Create image display
        self.image_display = wx.StaticBitmap(panel)

        # Add to sizer
        sizer.Add(self.open_btn, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(self.image_display, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)
        self.Centre()
        self.Show()

    def on_open(self, event):
        wildcard = "Images (*.jpg;*.png;*.bmp)|*.jpg;*.png;*.bmp"
        dialog = wx.FileDialog(self, "Choose an image", wildcard=wildcard)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.load_image(path)

        dialog.Destroy()

    def load_image(self, path):
        try:
            image = wx.Image(path)
            if image.IsOk():
                # Scale image if too large
                width, height = image.GetWidth(), image.GetHeight()
                max_size = 500

                if width > max_size or height > max_size:
                    if width > height:
                        new_width = max_size
                        new_height = int(height * max_size / width)
                    else:
                        new_height = max_size
                        new_width = int(width * max_size / height)
                    image = image.Scale(new_width, new_height)

                bitmap = wx.Bitmap(image)
                self.image_display.SetBitmap(bitmap)
                self.Layout()
        except Exception as e:
            wx.MessageBox(f"Error loading image: {e}", "Error")


if __name__ == "__main__":
    app = wx.App()
    frame = SimpleImageViewer()
    app.MainLoop()