import pandas as pd
import mysql.connector
from sklearn.naive_bayes import GaussianNB
from tkinter import *
from tkinter import ttk, messagebox

class CollegeRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Recommender System")
        self.root.geometry("1000x600")  # Increase the size of the window

        # Database connection
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nihaal2004",
            database="college1"
        )

        self.caste_options = [
            "OC_BOYS", "OCGIRLS", "BC_A_BOYS", "BC_A_GIRLS", "BC_B_BOYS", "BC_B_GIRLS",
            "BC_C_BOYS", "BC_C_GIRLS", "BC_D_BOYS", "BC_D_GIRLS", "BC_E_BOYS", "BC_E_GIRLS",
            "SC_BOYS", "SC_GIRLS", "ST_BOYS", "ST_GIRLS", "EWS_GEN_OU", "EWS_GIRLS_OU"
        ]

        self.create_widgets()
        self.fetch_data()

    def create_widgets(self):
        Label(self.root, text="Enter Rank:").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.rank_entry = Entry(self.root)
        self.rank_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self.root, text="Select Caste:").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        self.caste_combobox = ttk.Combobox(self.root, values=self.caste_options)
        self.caste_combobox.grid(row=1, column=1, padx=10, pady=10)

        Label(self.root, text="Select Branch Code:").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        self.branch_combobox = ttk.Combobox(self.root)
        self.branch_combobox.grid(row=2, column=1, padx=10, pady=10)

        Label(self.root, text="Select Place (Optional):").grid(row=3, column=0, padx=10, pady=10, sticky=W)
        self.place_combobox = ttk.Combobox(self.root)
        self.place_combobox.grid(row=3, column=1, padx=10, pady=10)

        self.recommend_button = Button(self.root, text="Recommend Colleges", command=self.recommend_colleges)
        self.recommend_button.grid(row=4, columnspan=2, pady=10)

        # Treeview for displaying results
        self.result_tree = ttk.Treeview(self.root, columns=("Institute", "Place", "Branch", "Rank", "Fee"), show="headings")
        self.result_tree.heading("Institute", text="Institute")
        self.result_tree.heading("Place", text="Place")
        self.result_tree.heading("Branch", text="Branch")
        self.result_tree.heading("Rank", text="Rank")
        self.result_tree.heading("Fee", text="Fee")
        self.result_tree.grid(row=5, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Set column widths to fit screen and allow full display of data
        self.result_tree.column("Institute", width=300)
        self.result_tree.column("Place", width=100)
        self.result_tree.column("Branch", width=100)
        self.result_tree.column("Rank", width=100)
        self.result_tree.column("Fee", width=100)

        # Configure row and column weights for expanding Treeview
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Add vertical scrollbar to Treeview
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.result_tree.yview)
        scrollbar.grid(row=5, column=2, sticky="ns")
        self.result_tree.configure(yscroll=scrollbar.set)

        self.finish_button = Button(self.root, text="Finish", command=self.finish)
        self.finish_button.grid(row=6, columnspan=2, pady=10)

    def fetch_data(self):
        query = "SELECT * FROM eamcet_finalr"
        self.df = pd.read_sql(query, self.connection)

        caste_columns = self.caste_options
        self.df[caste_columns] = self.df[caste_columns].apply(pd.to_numeric, errors='coerce')

        # Populate branch code options
        branch_codes = self.df['BranchCode'].unique().tolist()
        self.branch_combobox['values'] = branch_codes

        # Populate place options
        places = self.df['Place'].unique().tolist()
        self.place_combobox['values'] = places

        self.train_naive_bayes()

    def train_naive_bayes(self):
        self.model = GaussianNB()
        self.df.dropna(subset=self.caste_options, inplace=True)

        X = self.df[self.caste_options]
        y = self.df["BranchCode"]
        self.model.fit(X, y)

    def recommend_colleges(self):
        try:
            rank = int(self.rank_entry.get())
            caste = self.caste_combobox.get()
            branch_code = self.branch_combobox.get()
            place = self.place_combobox.get()

            if not caste:
                messagebox.showerror("Input Error", "Please select a caste.")
                return

            self.df['Rank'] = self.df[caste]
            filtered_df = self.df[(self.df['Rank'] >= rank) & (self.df['BranchCode'] == branch_code)]

            if place:
                filtered_df = filtered_df[filtered_df['Place'] == place]

            for row in self.result_tree.get_children():
                self.result_tree.delete(row)

            if filtered_df.empty:
                messagebox.showinfo("Result", "No colleges found matching the criteria.")
            else:
                for _, row in filtered_df.iterrows():
                    self.result_tree.insert("", "end", values=(row['Institute_Name'], row['Place'], row['BranchCode'], row[caste], row['Tuition_Fee']))
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid rank.")

    def finish(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        thank_you_page = ThankYouPage(self.root)


class WelcomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to College Suggestor")

        self.label = Label(self.root, text="Welcome to the College Suggestor System", font=("Helvetica", 24), pady=20)
        self.label.pack(pady=20)

        self.enter_button = Button(self.root, text="Find Colleges", command=self.enter_app, font=("Helvetica", 16))
        self.enter_button.pack(pady=20)

    def enter_app(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        app = CollegeRecommenderApp(self.root)


class ThankYouPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Thank You")

        self.label = Label(self.root, text="Thank you for using the College Suggestor System", font=("Helvetica", 24), pady=20)
        self.label.pack(expand=True)


def main():
    root = Tk()
    root.geometry("1000x600")  # Set window size to accommodate larger text area
    welcome_page = WelcomePage(root)
    root.mainloop()

if __name__ == "__main__":
    main()
