
$code = @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms;
public class SS {
    public static void Grab(string path) {
        Rectangle b = Screen.PrimaryScreen.Bounds;
        using (Bitmap bmp = new Bitmap(b.Width, b.Height, PixelFormat.Format32bppArgb)) {
            using (Graphics g = Graphics.FromImage(bmp)) {
                g.CopyFromScreen(b.Location, Point.Empty, b.Size);
            }
            bmp.Save(path, ImageFormat.Png);
        }
    }
}
"@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing, System.Windows.Forms
[SS]::Grab($args[0])
