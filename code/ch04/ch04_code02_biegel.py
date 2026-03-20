import requests

url = "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
headers = {"APIKey": "YOUR_API_KEY", "Accept": "application/json"}
params = {
    "$top": "5",
    "$select": "SalesOrder,SoldToParty,SalesOrderDate,TotalNetAmount",
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    orders = response.json()["d"]["results"]
    print(f"{len(orders)} Sales Orders from SAP:")

    for order in orders:
        so_id = order.get("SalesOrder", "N/A")
        customer = order.get("SoldToParty", "N/A")
        amount = order.get("TotalNetAmount", "N/A")
        print(f"  {so_id}: Customer {customer} - ${amount}")
else:
    print(f"Error: {response.status_code}")
