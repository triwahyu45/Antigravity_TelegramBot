
    [Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
    [Reflection.Assembly]::LoadWithPartialName("System.Drawing") | Out-Null
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save('G:\\Antigravity_Server\\Screenshots\\desktop_real_1785295922.png', [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    