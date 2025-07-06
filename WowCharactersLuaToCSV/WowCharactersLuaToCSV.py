import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import sys

class LuaToCsvConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Lua to CSV Converter")
        self.root.geometry("600x200")
        
        # Input file selection
        tk.Label(root, text="Input Lua File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_path = tk.Entry(root, width=50)
        self.input_path.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output file selection
        tk.Label(root, text="Output CSV File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_path = tk.Entry(root, width=50)
        self.output_path.grid(row=1, column=1, padx=5, pady=5)
        self.output_path.insert(0, "characters.csv")
        tk.Button(root, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Convert button
        tk.Button(root, text="Convert to CSV", command=self.convert, height=2).grid(row=2, column=1, pady=10)
        
        # Status label
        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.grid(row=3, column=0, columnspan=3, sticky=tk.EW+tk.S)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("Lua files", "*.lua")])
        if file_path:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, file_path)

    def convert(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
            
        try:
            with open(input_file, 'r') as f:
                content = f.read()
            
            # Extract character records section
            start_marker = "DataStore_Characters_Info = {"
            end_marker = "}\nDataStore_Characters_GuildRanks"
            
            if start_marker not in content or end_marker not in content:
                raise ValueError("Invalid file format: Markers not found")
                
            records_section = content.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()
            
            # Parse records
            records = self.parse_records(records_section)
            
            # Write CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = sorted(set().union(*(d.keys() for d in records)))
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
            
            self.status.config(text=f"Success! Created {output_file} with {len(records)} characters")
            messagebox.showinfo("Success", f"Converted {len(records)} characters to\n{output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text=f"Error: {str(e)}")

    def parse_records(self, records_section):
        records = []
        current_record = {}
        in_record = False
        
        for line in records_section.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line == '{':
                in_record = True
                current_record = {}
                continue
            elif line == '},' or line == '}':
                if in_record and current_record:
                    records.append(current_record)
                in_record = False
                continue
                
            if not in_record:
                continue
                
            if '=' not in line:
                continue
                
            key_part, value_part = line.split('=', 1)
            key_part = key_part.strip()
            value_part = value_part.strip().rstrip(',')
            
            if key_part.startswith('["') and key_part.endswith('"]'):
                key = key_part[2:-2]
            else:
                continue
                
            if value_part.startswith('"') and value_part.endswith('"'):
                value = value_part[1:-1]
            else:
                try:
                    value = int(value_part)
                except ValueError:
                    value = value_part
                    
            current_record[key] = value
            
        return records

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaToCsvConverter(root)
    root.mainloop()