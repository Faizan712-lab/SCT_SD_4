import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent

class ReliableScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Product Scraper")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.create_widgets()
        self.ua = UserAgent()
        self.products = []
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # URL Input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="Target URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Control Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.scrape_btn = ttk.Button(btn_frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        
        # Results Table
        self.tree = ttk.Treeview(main_frame, columns=('Name', 'Price', 'Rating', 'Category', 'Brand'), show='headings')
        
        # Configure columns
        columns = {
            'Name': {'width': 300, 'anchor': tk.W},
            'Price': {'width': 100, 'anchor': tk.CENTER},
            'Rating': {'width': 100, 'anchor': tk.CENTER},
            'Category': {'width': 200, 'anchor': tk.W},
            'Brand': {'width': 150, 'anchor': tk.W}
        }
        
        for col, params in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **params)
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def start_scraping(self):
        url = self.url_entry.get().strip()
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Please enter a valid URL starting with http:// or https://")
            return

        try:
            self.status.config(text="Connecting to website...")
            self.root.update_idletasks()
            
            # Randomize user agent
            headers = {'User-Agent': self.ua.random}
            
            # Fetch page content
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.status.config(text="Parsing content...")
            self.root.update_idletasks()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # DEMO SELECTORS - MUST BE UPDATED FOR TARGET WEBSITE
            product_cards = soup.select('div.product-item')  # Update this selector
            if not product_cards:
                messagebox.showwarning("Warning", "No products found - check CSS selectors")
                return

            self.status.config(text="Extracting product data...")
            self.products = []
            
            for card in product_cards:
                try:
                    product = {
                        'name': self.safe_extract(card, 'h2.product-title'),
                        'price': self.safe_extract(card, 'span.price'),
                        'rating': self.safe_extract(card, 'div.rating'),
                        'category': self.safe_extract(card, 'div.category'),
                        'brand': self.safe_extract(card, 'div.brand-name')
                    }
                    self.products.append(product)
                except Exception as e:
                    print(f"Error processing product: {str(e)}")

            self.update_table()
            self.save_to_csv()
            self.status.config(text=f"Success! Found {len(self.products)} products")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.status.config(text="Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            self.status.config(text="Ready")

    def safe_extract(self, element, selector):
        """Safely extract text from element with error handling"""
        result = element.select_one(selector)
        if result:
            return result.text.strip()
        return 'N/A'

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        for product in self.products:
            self.tree.insert('', 'end', values=(
                product['name'],
                product['price'],
                product['rating'],
                product['category'],
                product['brand']
            ))

    def save_to_csv(self):
        try:
            with open('products.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
                writer.writeheader()
                writer.writerows(self.products)
            messagebox.showinfo("Success", "Data saved to products.csv")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save CSV: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReliableScraperApp(root)
    root.mainloop()