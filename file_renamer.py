"""
Bulk File Renamer - A Python application for batch renaming files
Author: AI Assistant
Version: 1.0
"""

import os
import sys
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from datetime import datetime


class FileRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk File Renamer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.files = []
        self.directory = tk.StringVar()
        self.pattern = tk.StringVar()
        self.replacement = tk.StringVar()
        self.prefix = tk.StringVar()
        self.suffix = tk.StringVar()
        self.case_option = tk.StringVar(value="keep")
        self.numbering = tk.StringVar(value="none")
        self.number_start = tk.IntVar(value=1)
        self.number_padding = tk.IntVar(value=2)
        self.extension_option = tk.StringVar(value="keep")
        self.recursive = tk.BooleanVar(value=False)
        self.rename_in_progress = False
        
        # Setup UI
        self.setup_ui()
        self.update_preview()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Preview section expands
        
        # ===== Directory Selection =====
        dir_frame = ttk.LabelFrame(main_frame, text="Directory", padding="5")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.directory, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).grid(row=0, column=2)
        ttk.Button(dir_frame, text="Load Files", command=self.load_files).grid(row=0, column=3, padx=(5, 0))
        
        # ===== Rename Options =====
        options_frame = ttk.LabelFrame(main_frame, text="Rename Options", padding="5")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Row 0: Find/Replace
        ttk.Label(options_frame, text="Find:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(options_frame, textvariable=self.pattern, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Label(options_frame, text="Replace:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        ttk.Entry(options_frame, textvariable=self.replacement, width=30).grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # Row 1: Prefix/Suffix
        ttk.Label(options_frame, text="Prefix:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(options_frame, textvariable=self.prefix, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        ttk.Label(options_frame, text="Suffix:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(options_frame, textvariable=self.suffix, width=30).grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Row 2: Additional options
        ttk.Label(options_frame, text="Case:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        case_combo = ttk.Combobox(options_frame, textvariable=self.case_option, 
                                  values=["keep", "lower", "upper", "title"], width=10, state="readonly")
        case_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(options_frame, text="Numbering:").grid(row=2, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        num_combo = ttk.Combobox(options_frame, textvariable=self.numbering,
                                 values=["none", "prefix", "suffix", "replace"], width=10, state="readonly")
        num_combo.grid(row=2, column=3, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(options_frame, text="Start:").grid(row=2, column=4, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Spinbox(options_frame, from_=1, to=9999, textvariable=self.number_start, width=6).grid(row=2, column=5, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(options_frame, text="Padding:").grid(row=2, column=6, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Spinbox(options_frame, from_=1, to=10, textvariable=self.number_padding, width=6).grid(row=2, column=7, sticky=tk.W, pady=(5, 0))
        
        # Row 3: Extension and Recursive
        ttk.Label(options_frame, text="Extension:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ext_combo = ttk.Combobox(options_frame, textvariable=self.extension_option,
                                 values=["keep", "lower", "upper"], width=10, state="readonly")
        ext_combo.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        ttk.Checkbutton(options_frame, text="Include subdirectories", 
                       variable=self.recursive).grid(row=3, column=2, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Row 4: Action buttons
        action_frame = ttk.Frame(options_frame)
        action_frame.grid(row=4, column=0, columnspan=8, pady=(10, 0))
        
        ttk.Button(action_frame, text="Preview", command=self.update_preview).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Rename Files", command=self.start_rename).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Reset All", command=self.reset_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # ===== Preview Section =====
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Treeview for preview
        columns = ("#", "Original", "New", "Status")
        self.tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("#", text="#")
        self.tree.heading("Original", text="Original Name")
        self.tree.heading("New", text="New Name")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("#", width=50)
        self.tree.column("Original", width=250)
        self.tree.column("New", width=250)
        self.tree.column("Status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ===== Status Bar =====
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKNOWN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Bind events to update preview
        self.pattern.trace('w', lambda *args: self.update_preview())
        self.replacement.trace('w', lambda *args: self.update_preview())
        self.prefix.trace('w', lambda *args: self.update_preview())
        self.suffix.trace('w', lambda *args: self.update_preview())
        self.case_option.trace('w', lambda *args: self.update_preview())
        self.numbering.trace('w', lambda *args: self.update_preview())
        self.number_start.trace('w', lambda *args: self.update_preview())
        self.number_padding.trace('w', lambda *args: self.update_preview())
        self.extension_option.trace('w', lambda *args: self.update_preview())
        
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.directory.set(directory)
            self.load_files()
    
    def load_files(self):
        """Load files from the selected directory"""
        directory = self.directory.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
        
        self.files = []
        self.tree.delete(*self.tree.get_children())
        
        try:
            if self.recursive.get():
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, directory)
                        self.files.append({
                            'path': full_path,
                            'name': file,
                            'rel_path': rel_path
                        })
            else:
                for file in os.listdir(directory):
                    full_path = os.path.join(directory, file)
                    if os.path.isfile(full_path):
                        self.files.append({
                            'path': full_path,
                            'name': file,
                            'rel_path': file
                        })
            
            self.status_var.set(f"Loaded {len(self.files)} files")
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
    
    def apply_rename_rules(self, filename):
        """Apply all rename rules to a filename"""
        name, ext = os.path.splitext(filename)
        
        # Apply find/replace
        if self.pattern.get():
            pattern = self.pattern.get()
            replacement = self.replacement.get()
            try:
                # Try regex if pattern looks like regex
                if pattern.startswith('^') or pattern.endswith('$') or any(c in pattern for c in '.*+?[]{}()|'):
                    name = re.sub(pattern, replacement, name)
                else:
                    name = name.replace(pattern, replacement)
            except re.error:
                # Fall back to simple replace if regex fails
                name = name.replace(pattern, replacement)
        
        # Apply numbering
        numbering = self.numbering.get()
        if numbering != "none":
            # We'll apply numbering later as it needs context
            pass
        
        # Apply case conversion
        case = self.case_option.get()
        if case == "lower":
            name = name.lower()
        elif case == "upper":
            name = name.upper()
        elif case == "title":
            name = name.title()
        
        # Apply extension changes
        ext_option = self.extension_option.get()
        if ext_option == "lower":
            ext = ext.lower()
        elif ext_option == "upper":
            ext = ext.upper()
        
        return name, ext
    
    def update_preview(self):
        """Update the preview treeview with renamed files"""
        self.tree.delete(*self.tree.get_children())
        
        if not self.files:
            return
        
        # Sort files for consistent numbering
        sorted_files = sorted(self.files, key=lambda x: x['name'])
        
        # Apply numbering if needed
        numbering = self.numbering.get()
        start_num = self.number_start.get()
        padding = self.number_padding.get()
        num_width = max(padding, len(str(start_num + len(sorted_files) - 1)))
        
        preview_data = []
        for idx, file_info in enumerate(sorted_files):
            original_name = file_info['name']
            name, ext = self.apply_rename_rules(original_name)
            
            # Apply numbering
            if numbering == "prefix":
                num_str = str(start_num + idx).zfill(num_width)
                new_name = f"{num_str}_{name}{ext}"
            elif numbering == "suffix":
                num_str = str(start_num + idx).zfill(num_width)
                new_name = f"{name}_{num_str}{ext}"
            elif numbering == "replace":
                num_str = str(start_num + idx).zfill(num_width)
                new_name = f"{num_str}{ext}"
            else:
                new_name = f"{name}{ext}"
            
            # Apply prefix/suffix
            prefix = self.prefix.get()
            suffix = self.suffix.get()
            if prefix or suffix:
                base_name, base_ext = os.path.splitext(new_name)
                new_name = f"{prefix}{base_name}{suffix}{base_ext}"
            
            # Check for duplicates
            new_path = os.path.join(self.directory.get(), new_name) if not self.recursive.get() else None
            status = "OK"
            
            # Check if new name conflicts with existing file
            if new_name != original_name:
                if new_path and os.path.exists(new_path):
                    status = "⚠️ Conflict"
            
            preview_data.append({
                'index': idx + 1,
                'original': original_name,
                'new': new_name,
                'status': status,
                'file_info': file_info,
                'new_name': new_name
            })
        
        # Populate treeview
        for data in preview_data:
            self.tree.insert("", tk.END, values=(
                data['index'],
                data['original'],
                data['new'],
                data['status']
            ))
        
        # Store preview data for rename operation
        self.preview_data = preview_data
        
        # Update status
        conflicts = sum(1 for d in preview_data if d['status'] == "⚠️ Conflict")
        if conflicts:
            self.status_var.set(f"Preview: {len(preview_data)} files, {conflicts} conflicts detected")
        else:
            self.status_var.set(f"Preview: {len(preview_data)} files ready")
    
    def start_rename(self):
        """Start the rename process"""
        if self.rename_in_progress:
            return
        
        if not hasattr(self, 'preview_data') or not self.preview_data:
            messagebox.showwarning("Warning", "No files to rename. Please load files first.")
            return
        
        # Check for conflicts
        conflicts = [d for d in self.preview_data if d['status'] == "⚠️ Conflict"]
        if conflicts:
            result = messagebox.askyesno(
                "Conflicts Detected",
                f"There are {len(conflicts)} filename conflicts. Do you want to continue?\n\n"
                "Conflicting files will be skipped."
            )
            if not result:
                return
        
        # Start rename in separate thread to keep UI responsive
        self.rename_in_progress = True
        self.status_var.set("Renaming files...")
        threading.Thread(target=self.rename_files, daemon=True).start()
    
    def rename_files(self):
        """Perform the actual file renaming"""
        renamed_count = 0
        skipped_count = 0
        errors = []
        
        try:
            for data in self.preview_data:
                if data['status'] == "⚠️ Conflict":
                    skipped_count += 1
                    continue
                
                old_path = data['file_info']['path']
                new_name = data['new_name']
                
                # Get the directory from the old path
                dir_path = os.path.dirname(old_path)
                new_path = os.path.join(dir_path, new_name)
                
                # Skip if names are the same
                if old_path == new_path:
                    continue
                
                try:
                    os.rename(old_path, new_path)
                    renamed_count += 1
                    
                    # Update file info for future previews
                    data['file_info']['name'] = new_name
                    data['file_info']['path'] = new_path
                    
                except Exception as e:
                    errors.append(f"Failed to rename {os.path.basename(old_path)}: {str(e)}")
                    skipped_count += 1
            
            # Update UI
            self.root.after(0, self.rename_complete, renamed_count, skipped_count, errors)
            
        except Exception as e:
            self.root.after(0, self.rename_complete, renamed_count, skipped_count, [str(e)])
    
    def rename_complete(self, renamed, skipped, errors):
        """Handle completion of rename operation"""
        self.rename_in_progress = False
        
        # Refresh file list
        self.load_files()
        
        # Show results
        message = f"Rename complete!\n\nRenamed: {renamed} files\nSkipped: {skipped} files"
        if errors:
            message += f"\n\nErrors:\n{chr(10).join(errors[:5])}"
            if len(errors) > 5:
                message += f"\n... and {len(errors) - 5} more errors"
        
        messagebox.showinfo("Rename Complete", message)
        self.status_var.set(f"Rename complete. Renamed: {renamed}, Skipped: {skipped}")
    
    def reset_all(self):
        """Reset all input fields to default values"""
        self.pattern.set("")
        self.replacement.set("")
        self.prefix.set("")
        self.suffix.set("")
        self.case_option.set("keep")
        self.numbering.set("none")
        self.number_start.set(1)
        self.number_padding.set(2)
        self.extension_option.set("keep")
        self.recursive.set(False)
        self.update_preview()
        self.status_var.set("Reset complete")


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = FileRenamer(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
