import tkinter as tk
from tkinter import messagebox, filedialog
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv
import time
import undetected_chromedriver as uc


class ECommerceScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Commerce Scraper")
        self.root.geometry("600x500")
        
        tk.Label(root, text="Enter E-Commerce URL:", font=("Arial", 12)).pack(pady=10)
        self.url_entry = tk.Entry(root, width=80)
        self.url_entry.pack(pady=5)
        
        self.scrape_button = tk.Button(root, text="Scrape", command=self.scrape_data,
                                       font=("Arial", 12), bg="lightblue")
        self.scrape_button.pack(pady=5)
        
        self.save_button = tk.Button(root, text="Save to CSV", command=self.save_to_csv,
                                     font=("Arial", 12), bg="lightgreen")
        self.save_button.pack(pady=5)
        
        self.result_text = tk.Text(root, height=20, width=80)
        self.result_text.pack(pady=10)
        
        self.data = []  # To store scraped product information

    def scrape_data(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Scraping... Please wait.\n")
        self.root.update()

        try:
            # Set up Chrome options. Running in non-headless mode helps mimic real user behavior.
            options = uc.ChromeOptions()
            # Uncomment the next line to try headless mode (may be more detectable)
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = uc.Chrome(options=options)
            driver.get(url)
            # Allow time for the page to fully load; adjust as needed.
            time.sleep(5)

            page_source = driver.page_source
            driver.quit()

            soup = BeautifulSoup(page_source, "html.parser")
            products = []
            # NOTE: The selectors below are generic placeholders.
            # Adjust them to match the structure of your target e-commerce site.
            product_elements = soup.find_all("div", class_="product")
            if not product_elements:
                self.result_text.insert(tk.END, "No products found. The site may be using advanced blocking or a different structure.\n")
                return

            for prod in product_elements:
                name_tag = prod.find("h2", class_="product-name")
                price_tag = prod.find("span", class_="price")
                rating_tag = prod.find("span", class_="rating")
                product = {
                    "Name": name_tag.get_text(strip=True) if name_tag else "N/A",
                    "Price": price_tag.get_text(strip=True) if price_tag else "N/A",
                    "Rating": rating_tag.get_text(strip=True) if rating_tag else "N/A"
                }
                products.append(product)

            if not products:
                self.result_text.insert(tk.END, "Products were not extracted. Try adjusting the selectors.\n")
                return

            self.data = products
            self.result_text.delete("1.0", tk.END)
            for product in products:
                self.result_text.insert(tk.END, f"{product['Name']} - {product['Price']} - {product['Rating']}\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def save_to_csv(self):
        if not self.data:
            messagebox.showerror("Error", "No data to save. Please scrape first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=["Name", "Price", "Rating"])
                    writer.writeheader()
                    for row in self.data:
                        writer.writerow(row)
                messagebox.showinfo("Success", "Data saved to CSV successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ECommerceScraperGUI(root)
    root.mainloop()
