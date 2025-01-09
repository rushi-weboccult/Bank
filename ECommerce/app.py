from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'Secret123'

#
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT Id, Name, Price, Quantity FROM Products')
    products = c.fetchall()
    conn.close()
    return products

#
def get_product_by_id(product_id):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT Id, Name, Price, Quantity FROM Products WHERE Id = ?', (product_id,))
    product = c.fetchone()
    conn.close()
    return product

#
def change_product_quantity(product_id, new_quantity):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('UPDATE Products SET Quantity = ? WHERE Id = ?', (new_quantity, product_id))
    conn.commit()
    conn.close()

#
def calculate_total(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total

#
@app.route('/')
def index():
    products = get_products()  
    return render_template('index.html', products=products)

#
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    
    product = get_product_by_id(product_id)
    
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('index'))

    available_quantity = product[3]
    requested_quantity = int(request.form['quantity'])

    if requested_quantity > available_quantity:
        flash("Error: You cannot add more than the available quantity.", "danger")
    else:
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if product already in cart
        product_in_cart = next((item for item in session['cart'] if item['id'] == product[0]), None)
        
        if product_in_cart:
            product_in_cart['quantity'] += requested_quantity
        else:
            session['cart'].append({
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': requested_quantity
            })
        
        flash(f"Added {requested_quantity} {product[1]}(s) to your cart.", "success")

    return redirect(url_for('index'))

#
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total_amount = calculate_total(cart)
    return render_template('cart.html', cart=cart, total_amount=total_amount)

#
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))

#
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty. Add items to cart before proceeding.", "warning")
        return redirect(url_for('index'))
    
    total_amount = calculate_total(cart)
    return render_template('checkout.html', total_amount=total_amount)

#
def change_account_data(new_balance,accounts):
    conn = sqlite3.connect('/home/wot-rushi/Rushi/Learn/Bank_Final/Bank/Bank_Final.db')
    c = conn.cursor()
    c.execute('UPDATE Users SET Balance=? WHERE Account=?',(new_balance,accounts))
    conn.commit()
    conn.close()

def get_account_data(accounts):
    conn = sqlite3.connect('/home/wot-rushi/Rushi/Learn/Bank_Final/Bank/Bank_Final.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Users WHERE Account=?',(accounts,))
    #1|Rushi|1736329341|1234567890|9900|Rushi@20|1234
    data=c.fetchone()
    conn.close()
    return data

#
@app.route('/process_payment', methods=['POST'])
def process_payment():
    cart = session.get('cart', [])

    if not cart:
        flash("Your cart is empty. Add items to cart before proceeding.", "warning")
        return redirect(url_for('index'))
    
    total_amount = calculate_total(cart)

    account_number = request.form['account']
    pin_number = request.form['pin']
    
    datas=get_account_data(account_number)
    if datas:
        account_balance=datas[4]
        account_pin=datas[6]
    else:
        flash("Enter Correct Account Number.")
        return redirect(url_for('checkout'))

    if int(pin_number)!=account_pin:
        flash("Enter Correct Pin.")
        return redirect(url_for('checkout'))
    else:
        #check balance is available or not.....
        set_balance=account_balance-total_amount
        if set_balance>0:
            change_account_data(set_balance,account_number)
        else:
            flash("You do not have Sufficient balance.")
            return redirect(url_for('checkout'))            
        
    for item in cart:
        product = get_product_by_id(item['id'])
        new_quantity = product[3] - item['quantity'] 
        change_product_quantity(item['id'], new_quantity)
    
    session.pop('cart', None)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
