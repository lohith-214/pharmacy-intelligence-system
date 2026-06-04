import pandas as pd 
import random 

# sample medicine names 
medicines = [
    "Paracetamol",
    "Dolo 650",
    "Azithromycin",
    "Vitamin C",
    "Cough Syrup",
]

# Empty list to store rows
sales_data = []

# Generate 10 rows
for i in range(10):

    invoice_id = f"INV{i+1}"
    medicine = random.choice(medicines)
    quantity = random.randint(1, 5)
    price = random.randint(50, 500)

    sales_data.append([
        invoice_id,
        medicine,
        quantity,
        price
    ])

    # Create dataframe
    df = pd.DataFrame(
        sales_data,
        columns = [
            "invoice_id",
            "medicine",
            "quantity",
            "price"
        ]
    )

    # print dataframe
    print(df)
    