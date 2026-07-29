using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms;
using System.Runtime.InteropServices;

class ScreenGrabber {
    [DllImport("user32.dll")]
    private static extern bool SetProcessDPIAware();

    static void Main(string[] args) {
        try {
            SetProcessDPIAware();
            string outPath = args.Length > 0 ? args[0] : "desktop_screengrab.png";
            
            // Get virtual screen bounds for multi-monitor / primary screen
            int left = SystemInformation.VirtualScreen.Left;
            int top = SystemInformation.VirtualScreen.Top;
            int width = SystemInformation.VirtualScreen.Width;
            int height = SystemInformation.VirtualScreen.Height;

            using (Bitmap bitmap = new Bitmap(width, height, PixelFormat.Format32bppArgb)) {
                using (Graphics g = Graphics.FromImage(bitmap)) {
                    g.CopyFromScreen(left, top, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
                }
                bitmap.Save(outPath, ImageFormat.Png);
            }
            Console.WriteLine("SUCCESS:" + outPath);
        } catch (Exception ex) {
            Console.WriteLine("ERROR:" + ex.Message);
        }
    }
}
