# Bank and E-commerce Integration System
This project consists of two separate websites: a Banking System and an E-commerce Platform for purchasing IT hardware. The backend of both systems is connected, allowing customers to make secure transactions and purchases using their bank account information.

## Features
### Bank Website:

- **User Registration & Login:** Allows users to create an account and log in securely.
- **Transactions:** Users can make deposits and withdrawals, with restrictions ensuring they cannot withdraw more than their current balance.
- **Check Balance:** Users can view their account balance.
- **Change Password:** Users can update their password for security.

### E-commerce Website:

- **Browse IT Hardware:** Customers can browse and add IT hardware items (like laptops, peripherals, etc.) to their shopping cart.
- **Bank Integration for Payments:** When purchasing items, users are required to provide their Bank Account Number and PIN (password). This allows the system to check the available balance and deduct the purchase amount directly from the bank account.

## How it Works:

**1) Registration and Login:** <br/>
The user creates an account on the Bank Website and logs in to access their banking information.

**2) Transaction Handling:** <br/>
The user can deposit or withdraw money via the Bank website, with transaction limits based on the current balance.

**3) Shopping on E-commerce Website:** <br/>
The user browses products on the E-commerce Platform, adds items to their cart, and proceeds to checkout.<br/>
At checkout, the user enters their Bank Account Number and PIN to verify the transaction.<br/>
The E-commerce Backend then checks the provided credentials against the Bank Website Backend to validate the account balance.<br/>
If the user has enough funds, the purchase is completed and the amount is deducted from their bank account.<br/>

## Technologies Used:
- **Frontend:** HTML, CSS, JavaScript 
- **Backend:** Python (Flask)
- **Database:** SQLite
