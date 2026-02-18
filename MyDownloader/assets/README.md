# Assets Directory

This folder contains application resources.

## Structure

```
assets/
├── icons/
│   ├── app_icon.ico          # Main application icon (256x256)
│   ├── download.ico          # Download button icon
│   ├── queue.ico             # Queue icon
│   └── settings.ico          # Settings icon
│
└── images/
    ├── logo.png              # Application logo
    ├── banner.png            # About page banner
    └── screenshots/          # Application screenshots
        ├── main_window.png
        ├── download_tab.png
        ├── queue_tab.png
        └── settings_tab.png
```

## Icon Requirements

### app_icon.ico
- **Format**: ICO (Windows Icon)
- **Sizes**: 16x16, 32x32, 48x48, 256x256
- **Purpose**: Application icon, shown in taskbar, window title, installer

### Creating Icons

#### Online Tools:
- https://convertio.co/png-ico/
- https://icoconvert.com/
- https://www.favicon-generator.org/

#### With Python:
```python
from PIL import Image

img = Image.open('source.png')
img.save('app_icon.ico', format='ICO', sizes=[
    (16, 16),
    (32, 32),
    (48, 48),
    (256, 256)
])
```

#### With GIMP:
1. Open image
2. Image → Scale → 256x256
3. File → Export As → .ico
4. Select all sizes in dialog

## Images

### Logo (logo.png)
- **Size**: 512x512 px
- **Format**: PNG with transparency
- **Purpose**: About tab, splash screen

### Banner (banner.png)
- **Size**: 800x200 px
- **Format**: PNG
- **Purpose**: About tab header

## Notes

- All images should be optimized for size (use tools like TinyPNG)
- Icons should have transparent backgrounds
- Use consistent color scheme matching app theme
- High-DPI ready (provide @2x versions if needed)

## Placeholder

Until custom icons are created, the application will use:
- Emoji icons (📥, 📑, 📜, ⚙️, etc.)
- Default Windows icons
- TTK default themes

## License

Make sure all images used have appropriate licenses or are created by you.
