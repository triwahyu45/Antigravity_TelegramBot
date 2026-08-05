"""
Google Antigravity Telegram Remote Control Bridge
Windows Show/Hide Window Toggle Helper Engine

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os, subprocess

def hide_antigravity_window():
    ps_cmd = r"""
$code = @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinSearch {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static int HideAntigravity() {
        int count = 0;
        EnumWindows((hWnd, lParam) => {
            StringBuilder cls = new StringBuilder(256);
            GetClassName(hWnd, cls, 256);
            int len = GetWindowTextLength(hWnd);
            StringBuilder sb = new StringBuilder(len + 1);
            if (len > 0) GetWindowText(hWnd, sb, len + 1);
            
            string title = sb.ToString().ToLower();
            string cname = cls.ToString();
            
            if (cname == "Chrome_WidgetWin_1" || title.Contains("antigravity") || title.Contains("wahyu")) {
                if (title.Contains("antigravity") || title.Contains("wahyu") || title == "") {
                    ShowWindow(hWnd, 0); // SW_HIDE (0)
                    count++;
                }
            }
            return true;
        }, IntPtr.Zero);
        return count;
    }
}
"@
Add-Type -TypeDefinition $code
[WinSearch]::HideAntigravity()
"""
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, creationflags=0x08000000)
        return True
    except Exception as e:
        print("[HIDE ERR]", e)
    return False

def show_antigravity_window():
    ps_cmd = r"""
$code = @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinSearch {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static int ShowAntigravity() {
        int count = 0;
        EnumWindows((hWnd, lParam) => {
            StringBuilder cls = new StringBuilder(256);
            GetClassName(hWnd, cls, 256);
            int len = GetWindowTextLength(hWnd);
            StringBuilder sb = new StringBuilder(len + 1);
            if (len > 0) GetWindowText(hWnd, sb, len + 1);
            
            string title = sb.ToString().ToLower();
            string cname = cls.ToString();
            
            if (cname == "Chrome_WidgetWin_1" || title.Contains("antigravity") || title.Contains("wahyu")) {
                if (title.Contains("antigravity") || title.Contains("wahyu")) {
                    ShowWindow(hWnd, 9); // SW_RESTORE (9)
                    ShowWindow(hWnd, 3); // SW_MAXIMIZE (3)
                    count++;
                }
            }
            return true;
        }, IntPtr.Zero);
        return count;
    }
}
"@
Add-Type -TypeDefinition $code
[WinSearch]::ShowAntigravity()
"""
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, creationflags=0x08000000)
        return True
    except Exception as e:
        print("[SHOW ERR]", e)
    return False
