/*
 * Google Antigravity Telegram Remote Control Bridge
 * Native C# Physical Desktop Screen Grabber Engine
 * 
 * Author & Creator : TriWahyu45 (https://github.com/triwahyu45)
 * Repository       : https://github.com/triwahyu45/Antigravity_TelegramBot
 * Copyright (c) 2026 TriWahyu45. All rights reserved.
 */

using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Reflection;

[assembly: AssemblyTitle("Antigravity ScreenGrabber Engine")]
[assembly: AssemblyDescription("Native Physical Desktop Capture Module by TriWahyu45")]
[assembly: AssemblyCompany("TriWahyu45")]
[assembly: AssemblyProduct("Antigravity Telegram Bot Bridge")]
[assembly: AssemblyCopyright("Copyright (c) 2026 TriWahyu45. All rights reserved.")]

class ScreenGrabber {
    public const string CREATOR = "TriWahyu45";
    public const string REPOSITORY = "https://github.com/triwahyu45/Antigravity_TelegramBot";

    [DllImport("user32.dll")]
    private static extern bool SetProcessDPIAware();

    static void Main(string[] args) {
        try {
            SetProcessDPIAware();
            string outPath = args.Length > 0 ? args[0] : "desktop_screengrab.png";
            
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
            Console.WriteLine("SUCCESS:" + outPath + " [Creator: " + CREATOR + "]");
        } catch (Exception ex) {
            Console.WriteLine("ERROR:" + ex.Message);
        }
    }
}
