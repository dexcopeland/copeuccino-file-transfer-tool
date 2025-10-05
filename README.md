# Copeuccino File Transfer Tool

A user-friendly GUI application for efficiently copying files between drives with maximum compatibility across Windows, Mac, and Linux systems.

## Features

### **Core Functionality**
- **Intuitive GUI** - Easy-to-use interface built with tkinter
- **Responsive design** - Scrollable interface that works on any screen size
- **Professional appearance** - Consistent background colors and visual theme
- **Multi-source selection** - Add individual files or entire folders
- **Smart drive detection** - Automatically identifies external drives
- **Cross-platform compatibility** - Works on Windows, Mac, and Linux

### **File Management**
- **Complete folder copying** - When adding folders, the entire folder (including its name) is copied
- **Flat copy option** - Copy all files to a single destination folder
- **Duplicate handling** - Automatically renames duplicates or overwrites based on preference
- **File verification** - MD5 checksum verification ensures data integrity

### **Drive Compatibility**
- **Universal file systems** - Optimized for FAT32, exFAT, and NTFS
- **External drive detection** - Highlights removable drives for easy identification
- **Drive information** - Shows total size, free space, and file system type
- **Real-time drive refresh** - Updates drive list without restarting

### 📊 **Progress Tracking**
- **Real-time progress bar** - Visual feedback during transfers
- **File-by-file status** - Shows currently copying file
- **Transfer statistics** - Displays files transferred and total size
- **Cancellation support** - Stop transfers at any time

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup
1. **Clone or download** this repository
2. **Navigate** to the project directory:
   ```bash
   cd copeuccino-file-transfer
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Windows Additional Setup
On Windows, the application uses `pywin32` for enhanced drive detection. This is automatically installed via requirements.txt.

## Usage

### Starting the Application
```bash
python copeuccino-file-transfer.py
```

### Basic Workflow
1. **Add Source Files**
   - Click "Add Files" to select individual files
   - Click "Add Folder (with contents)" to select entire directories (preserves folder name)
   - Use "Remove Selected" or "Clear All" to manage your selection

2. **Choose Destination**
   - Select from the "Available Drives" list (external drives highlighted in green)
   - Or use "Custom Path" to browse for any destination folder

3. **Configure Options**
   - ✅ **Verify file integrity** - Ensures copied files match originals
   - ✅ **Preserve folder structure** - Maintains directory hierarchy
   - ⬜ **Overwrite existing files** - Replace duplicates or create numbered copies

4. **Start Transfer**
   - Click "Start Transfer" to begin copying
   - Monitor progress with the real-time progress bar
   - Cancel anytime if needed

## Cross-Platform Compatibility

### File System Recommendations
- **exFAT** - Best for large files, works on all systems
- **FAT32** - Maximum compatibility, 4GB file size limit
- **NTFS** - Windows native, read-only on Mac (without additional software)

### Platform-Specific Features
- **Windows**: Enhanced drive type detection using Win32 API
- **Mac/Linux**: Mount point analysis for external drive identification
- **All Platforms**: Universal file operations and GUI components

## Technical Details

### Dependencies
- **psutil** - Cross-platform system and process utilities
- **tkinter** - Built-in Python GUI framework (included with Python)
- **pywin32** - Windows-specific enhancements (Windows only)

### Performance Features
- **Chunked copying** - 64KB chunks for optimal performance
- **Threading** - Non-blocking UI during transfers
- **Memory efficient** - Handles large files without excessive RAM usage
- **Progress callbacks** - Real-time transfer feedback

### Security Features
- **Checksum verification** - MD5 hash comparison ensures data integrity
- **Safe file handling** - Proper error handling and resource cleanup
- **Permission respect** - Skips inaccessible files gracefully

## Troubleshooting

### Common Issues
1. **"Permission denied" errors**
   - Run as administrator (Windows) or with sudo (Mac/Linux)
   - Check file/folder permissions

2. **Drive not detected**
   - Click "Refresh Drives" button
   - Ensure drive is properly mounted
   - Check if drive is accessible in file manager

3. **Transfer fails**
   - Verify destination has sufficient free space
   - Check if files are in use by other applications
   - Ensure destination drive is writable

### Performance Tips
- **Use exFAT** for best cross-platform performance
- **Close other applications** during large transfers
- **Use USB 3.0+ ports** for external drives
- **Disable antivirus scanning** temporarily for faster transfers

## License

This project is open source and available under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Made with ☕ for seamless cross-platform file transfers**
