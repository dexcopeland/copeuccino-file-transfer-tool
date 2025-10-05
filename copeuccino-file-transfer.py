#!/usr/bin/env python3
"""
Copeuccino File Transfer Tool
A user-friendly GUI application for efficiently copying files between drives
with maximum compatibility across Windows, Mac, and Linux systems.

Copyright (c) 2025 Copeuccino File Transfer Tool
Licensed under the MIT License - see LICENSE file for details.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import time
from pathlib import Path
import platform
import psutil
from typing import List, Dict, Optional
import hashlib


class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Copeuccino File Transfer Tool")
        self.root.geometry("800x600")
        self.root.minsize(500, 300)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.source_files = []
        self.destination_path = tk.StringVar()
        self.transfer_active = False
        self.cancel_transfer = False
        
        self.setup_ui()
        self.refresh_drives()
        
    def setup_ui(self):
        """Create the main user interface with scrollable content"""
        # Create main canvas and scrollbar for scrollable content
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Set canvas background to match UI theme
        try:
            bg_color = self.style.lookup('TFrame', 'background')
            if not bg_color or bg_color == '':  # Fallback if theme lookup fails
                bg_color = self.root.cget('bg')
            # Handle system default colors on different platforms
            if bg_color in ['SystemButtonFace', 'systemWindowBackgroundColor']:
                if platform.system() == "Windows":
                    bg_color = '#f0f0f0'
                elif platform.system() == "Darwin":  # macOS
                    bg_color = '#ececec'
                else:  # Linux
                    bg_color = '#d9d9d9'
        except:
            bg_color = '#f0f0f0'  # Light gray fallback
        
        self.canvas.configure(bg=bg_color)
        # Also set root window background to match
        self.root.configure(bg=bg_color)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Bind canvas resize to update frame width
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.root.bind("<MouseWheel>", self._on_mousewheel)
        
        # Main container (now inside scrollable frame)
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Copeuccino File Transfer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source section
        ttk.Label(main_frame, text="Source Files:", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Source files frame
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        
        # Source files listbox with scrollbar
        listbox_frame = ttk.Frame(source_frame)
        listbox_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.source_listbox = tk.Listbox(listbox_frame, height=4, selectmode=tk.EXTENDED)
        scrollbar_y = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        scrollbar_x = ttk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL, command=self.source_listbox.xview)
        
        self.source_listbox.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.source_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        listbox_frame.rowconfigure(0, weight=1)
        
        # Source buttons
        source_btn_frame = ttk.Frame(source_frame)
        source_btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Configure button frame for responsive layout
        for i in range(4):
            source_btn_frame.columnconfigure(i, weight=1)
        
        ttk.Button(source_btn_frame, text="Add Files", 
                  command=self.add_files).grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(source_btn_frame, text="Add Folder (with contents)", 
                  command=self.add_folder).grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(source_btn_frame, text="Remove Selected", 
                  command=self.remove_selected).grid(row=1, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(source_btn_frame, text="Clear All", 
                  command=self.clear_all).grid(row=1, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        # Destination section
        ttk.Label(main_frame, text="Destination:", font=('Arial', 12, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        # Available drives
        drives_frame = ttk.LabelFrame(main_frame, text="Available Drives", padding="5")
        drives_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        drives_frame.columnconfigure(0, weight=1)
        
        # Drives treeview
        self.drives_tree = ttk.Treeview(drives_frame, height=4, columns=('Size', 'Free', 'Type'), show='tree headings')
        self.drives_tree.heading('#0', text='Drive')
        self.drives_tree.heading('Size', text='Total Size')
        self.drives_tree.heading('Free', text='Free Space')
        self.drives_tree.heading('Type', text='File System')
        
        self.drives_tree.column('#0', width=200)
        self.drives_tree.column('Size', width=100)
        self.drives_tree.column('Free', width=100)
        self.drives_tree.column('Type', width=100)
        
        drives_scrollbar = ttk.Scrollbar(drives_frame, orient=tk.VERTICAL, command=self.drives_tree.yview)
        self.drives_tree.configure(yscrollcommand=drives_scrollbar.set)
        
        self.drives_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        drives_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.drives_tree.bind('<<TreeviewSelect>>', self.on_drive_select)
        
        # Refresh drives button
        ttk.Button(drives_frame, text="Refresh Drives", 
                  command=self.refresh_drives).grid(row=1, column=0, pady=5)
        
        # Custom destination
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dest_frame, text="Custom Path:").grid(row=0, column=0, padx=(0, 5))
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.destination_path)
        self.dest_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(dest_frame, text="Browse", 
                  command=self.browse_destination).grid(row=0, column=2, padx=(5, 0))
        
        # Transfer options
        options_frame = ttk.LabelFrame(main_frame, text="Transfer Options", padding="5")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.verify_checksum = tk.BooleanVar(value=True)
        self.preserve_structure = tk.BooleanVar(value=True)
        self.overwrite_existing = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Verify file integrity (checksum)", 
                       variable=self.verify_checksum).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Preserve folder structure", 
                       variable=self.preserve_structure).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.overwrite_existing).grid(row=2, column=0, sticky=tk.W)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to transfer files")
        self.status_label.grid(row=1, column=0, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Configure button frame for responsive layout
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        self.transfer_btn = ttk.Button(button_frame, text="Start Transfer", 
                                     command=self.start_transfer, style='Accent.TButton')
        self.transfer_btn.grid(row=0, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                   command=self.cancel_transfer_action, state=tk.DISABLED)
        self.cancel_btn.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights for main frame
        for i in range(9):
            main_frame.rowconfigure(i, weight=0)
        main_frame.rowconfigure(2, weight=1)  # Source listbox
        main_frame.rowconfigure(4, weight=1)  # Drives tree
    
    def get_drives(self) -> List[Dict]:
        """Get list of available drives with their information"""
        drives = []
        
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Format sizes
                    total_size = self.format_bytes(usage.total)
                    free_space = self.format_bytes(usage.free)
                    
                    # Determine if it's likely an external drive
                    is_external = self.is_external_drive(partition)
                    
                    drives.append({
                        'path': partition.mountpoint,
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'total': total_size,
                        'free': free_space,
                        'free_bytes': usage.free,
                        'is_external': is_external
                    })
                except (PermissionError, OSError):
                    # Skip drives that can't be accessed
                    continue
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get drive information: {str(e)}")
            
        return drives
    
    def is_external_drive(self, partition) -> bool:
        """Determine if a drive is likely external"""
        # This is a heuristic approach
        if platform.system() == "Windows":
            # On Windows, check if it's a removable drive
            import win32file
            try:
                drive_type = win32file.GetDriveType(partition.mountpoint)
                return drive_type == win32file.DRIVE_REMOVABLE
            except:
                # Fallback: assume drives other than C: might be external
                return not partition.mountpoint.upper().startswith('C:')
        else:
            # On Unix-like systems, check mount point
            external_paths = ['/media', '/mnt', '/Volumes']
            return any(partition.mountpoint.startswith(path) for path in external_paths)
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def refresh_drives(self):
        """Refresh the drives list"""
        # Clear existing items
        for item in self.drives_tree.get_children():
            self.drives_tree.delete(item)
        
        drives = self.get_drives()
        
        for drive in drives:
            # Add visual indicator for external drives
            display_name = drive['path']
            if drive['is_external']:
                display_name += " (External)"
            
            self.drives_tree.insert('', 'end', text=display_name,
                                  values=(drive['total'], drive['free'], drive['fstype']),
                                  tags=('external' if drive['is_external'] else 'internal',))
        
        # Configure tags for visual distinction
        self.drives_tree.tag_configure('external', background='lightgreen')
        self.drives_tree.tag_configure('internal', background='lightblue')
    
    def on_drive_select(self, event):
        """Handle drive selection"""
        selection = self.drives_tree.selection()
        if selection:
            item = self.drives_tree.item(selection[0])
            drive_path = item['text'].split(' (')[0]  # Remove (External) suffix if present
            self.destination_path.set(drive_path)
    
    def add_files(self):
        """Add files to the source list"""
        files = filedialog.askopenfilenames(
            title="Select files to transfer",
            filetypes=[("All files", "*.*")]
        )
        
        for file_path in files:
            if file_path not in self.source_files:
                self.source_files.append(file_path)
                self.source_listbox.insert(tk.END, file_path)
    
    def add_folder(self):
        """Add a folder (with all its contents) to the source list"""
        folder_path = filedialog.askdirectory(title="Select folder to transfer")
        
        if folder_path and folder_path not in self.source_files:
            self.source_files.append(folder_path)
            self.source_listbox.insert(tk.END, f"{folder_path} (Folder)")
    
    def remove_selected(self):
        """Remove selected items from the source list"""
        selected_indices = self.source_listbox.curselection()
        
        # Remove in reverse order to maintain indices
        for index in reversed(selected_indices):
            self.source_listbox.delete(index)
            del self.source_files[index]
    
    def clear_all(self):
        """Clear all source files"""
        self.source_files.clear()
        self.source_listbox.delete(0, tk.END)
    
    def browse_destination(self):
        """Browse for destination folder"""
        folder_path = filedialog.askdirectory(title="Select destination folder")
        if folder_path:
            self.destination_path.set(folder_path)
    
    def calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def copy_file_with_progress(self, src: str, dst: str, callback=None):
        """Copy file with progress tracking"""
        if os.path.isfile(src):
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            # Check if file exists and handle overwrite option
            if os.path.exists(dst) and not self.overwrite_existing.get():
                base, ext = os.path.splitext(dst)
                counter = 1
                while os.path.exists(f"{base}_{counter}{ext}"):
                    counter += 1
                dst = f"{base}_{counter}{ext}"
            
            # Copy file in chunks with progress
            file_size = os.path.getsize(src)
            copied = 0
            
            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                while True:
                    if self.cancel_transfer:
                        return False
                    
                    chunk = fsrc.read(64 * 1024)  # 64KB chunks
                    if not chunk:
                        break
                    
                    fdst.write(chunk)
                    copied += len(chunk)
                    
                    if callback:
                        callback(copied, file_size)
            
            # Verify checksum if enabled
            if self.verify_checksum.get():
                src_checksum = self.calculate_md5(src)
                dst_checksum = self.calculate_md5(dst)
                
                if src_checksum != dst_checksum:
                    raise Exception(f"Checksum verification failed for {os.path.basename(src)}")
            
            return True
        return False
    
    def get_all_files(self, path: str) -> List[str]:
        """Get all files from a path (file or directory)"""
        files = []
        
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        
        return files
    
    def start_transfer(self):
        """Start the file transfer process"""
        if not self.source_files:
            messagebox.showwarning("Warning", "Please select files to transfer")
            return
        
        if not self.destination_path.get():
            messagebox.showwarning("Warning", "Please select a destination")
            return
        
        if not os.path.exists(self.destination_path.get()):
            messagebox.showerror("Error", "Destination path does not exist")
            return
        
        # Start transfer in a separate thread
        self.transfer_active = True
        self.cancel_transfer = False
        self.transfer_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        transfer_thread = threading.Thread(target=self.transfer_files)
        transfer_thread.daemon = True
        transfer_thread.start()
    
    def transfer_files(self):
        """Transfer files in a separate thread"""
        try:
            # Collect all files to transfer
            all_files = []
            for source_path in self.source_files:
                all_files.extend(self.get_all_files(source_path))
            
            total_files = len(all_files)
            total_size = sum(os.path.getsize(f) for f in all_files if os.path.isfile(f))
            
            transferred_files = 0
            transferred_size = 0
            
            self.root.after(0, lambda: self.status_label.config(
                text=f"Transferring {total_files} files ({self.format_bytes(total_size)})..."))
            
            for file_path in all_files:
                if self.cancel_transfer:
                    break
                
                # Calculate destination path
                if self.preserve_structure.get():
                    # Find the source root for this file
                    source_root = None
                    for source_path in self.source_files:
                        if file_path.startswith(source_path):
                            source_root = source_path
                            break
                    
                    if source_root:
                        if os.path.isfile(source_root):
                            # Single file
                            rel_path = os.path.basename(file_path)
                        else:
                            # Directory - preserve the folder name in destination
                            folder_name = os.path.basename(source_root)
                            rel_path_from_source = os.path.relpath(file_path, source_root)
                            rel_path = os.path.join(folder_name, rel_path_from_source)
                        
                        dest_file = os.path.join(self.destination_path.get(), rel_path)
                    else:
                        dest_file = os.path.join(self.destination_path.get(), os.path.basename(file_path))
                else:
                    # Flat structure
                    dest_file = os.path.join(self.destination_path.get(), os.path.basename(file_path))
                
                # Update status
                self.root.after(0, lambda f=file_path: self.status_label.config(
                    text=f"Copying: {os.path.basename(f)}"))
                
                # Copy file with progress tracking
                file_size = os.path.getsize(file_path)
                
                def progress_callback(copied, total):
                    nonlocal transferred_size
                    progress = ((transferred_size + copied) / total_size) * 100
                    self.root.after(0, lambda: self.progress_var.set(progress))
                
                success = self.copy_file_with_progress(file_path, dest_file, progress_callback)
                
                if success:
                    transferred_files += 1
                    transferred_size += file_size
                    
                    # Update overall progress
                    progress = (transferred_size / total_size) * 100
                    self.root.after(0, lambda: self.progress_var.set(progress))
            
            # Transfer complete
            if self.cancel_transfer:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Transfer cancelled. {transferred_files}/{total_files} files transferred."))
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Transfer complete! {transferred_files} files transferred successfully."))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Transfer complete!\n{transferred_files} files transferred successfully."))
        
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Transfer failed: {str(e)}"))
        
        finally:
            self.transfer_active = False
            self.root.after(0, lambda: self.transfer_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.cancel_btn.config(state=tk.DISABLED))
    
    def cancel_transfer_action(self):
        """Cancel the ongoing transfer"""
        self.cancel_transfer = True
        self.status_label.config(text="Cancelling transfer...")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Try to set a modern theme
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        pass  # Fall back to default theme
    
    app = FileTransferApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
