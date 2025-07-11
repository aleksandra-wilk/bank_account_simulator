from flask import redirect, render_template, request, session, url_for, flash, jsonify
from decimal import Decimal
from app import app, db
from models import Client, Account, Card, Credit, Transaction
from models import create_account_db, create_card_db, create_client_db, create_credit_db, create_transaction_db
from math import pow
import random
import pandas as pd
from datetime import datetime, timedelta


# Strona logowania
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        
        # Wstępnie zdefiniowany użytkownik
        LOGIN = "admin"
        PASSWORD = "admin"

        username = request.form.get('username')
        client_id = request.form.get('username')
        password = request.form.get('password')

        # Weryfikacja użytkownika
        if username == LOGIN and password == PASSWORD:
            # Logowanie udane - zapisanie użytkownika w sesji
            session['username'] = username
            session['client_id'] = client_id
            return redirect(url_for('home'))
        else:
            # Nieudane logowanie
            flash("Nieprawidłowa nazwa użytkownika lub hasło.", "danger")

    return render_template('login.html')

# Strona główna
@app.route('/home', methods=['GET'])
def home():
    return render_template('home_page.html')


# Produkty - Konta
@app.route('/products/accounts', methods=['GET'])
def products_accounts():
    accounts = db.session.query(Account).all() 

    for account in accounts:
        account.account_nr = str(account.account_nr)
        account.account_nr = f"{account.account_nr[:2]} {account.account_nr[2:6]} {account.account_nr[6:10]} {account.account_nr[10:14]} {account.account_nr[14:18]}"

        if account.card_nr != None:
            account.card_nr = str(account.card_nr)
            account.card_nr = f"{account.card_nr[:4]} {account.card_nr[4:8]} {account.card_nr[8:12]} {account.card_nr[12:16]}"

    return render_template('products_accounts.html', accounts=accounts)


# Produkty - Założenie Konta
@app.route('/products/accounts/new', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        
        account_type = request.form.get('account_type')
        client_id = session.get('client_id')
        want_card = request.form.get('want_card')

        card_nr = None
        if want_card:
            card_nr = random.randint(1155_0900_0000_0000, 1155_0900_9999_9999)
            
        new_account = create_account_db(account_type, client_id, card_nr)
        
        db.session.add(new_account)
        db.session.commit()

        return render_template('create_account.html', message="Konto założono pomyślnie.")

    elif request.method == 'GET':
        return render_template('create_account.html')


# Produkty - Karty
@app.route('/products/cards', methods=['GET'])
def products_cards():

    cards = db.session.query(Card).all()

    for card in cards:
        card.account_nr = str(card.account_nr)
        card.account_nr = f"{card.account_nr[:2]} {card.account_nr[2:6]} {card.account_nr[6:10]} {card.account_nr[10:14]} {card.account_nr[14:18]}"

        card.card_nr = str(card.card_nr)
        card.card_nr = f"{card.card_nr[:4]} {card.card_nr[4:8]} {card.card_nr[8:12]} {card.card_nr[12:16]}"

    return render_template('products_cards.html', cards=cards)


# Produkty - Założenie Karty
@app.route('/products/cards/new', methods=['GET', 'POST'])
def create_card():
    if request.method == 'POST':
        account_nr = request.form.get('account_nr')
        account = db.session.query(Account).filter(Account.account_nr == account_nr).first()

        if account and account.card_nr is None: 
            account_type = account.account_type
            balance = account.balance
            new_card = create_card_db(account_nr, account_type, balance)
            account.card_nr = new_card.card_nr

            flash("Karta założona pomyślnie.", "success")
            return redirect(url_for('create_card'))

    accounts = db.session.query(Account).filter(Account.card_nr == None).all()
    return render_template('create_card.html', accounts=accounts)


# Oferty - Dodanie kredytu
@app.route('/products/loan/new', methods=['GET', 'POST'])
def create_credit():
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)  

        account = db.session.query(Account).filter(Account.account_type == 'current').first()

        if not account:
            flash("Nie znaleziono dostępnego konta do przypisania kredytu.", "danger")
            return redirect(url_for('create_credit'))

        create_credit_db(account.account_nr, amount) 

        flash("Kredyt został pomyślnie założony.", "success")
        return redirect(url_for('loan'))

    return render_template('loan.html')


# Produkty - Pożyczki
@app.route('/products/loans')
def products_loans():

    credits = db.session.query(Credit).all()

    for credit in credits:
        credit.account_nr = str(credit.account_nr)
        credit.account_nr = f"{credit.account_nr[:2]} {credit.account_nr[2:6]} {credit.account_nr[6:10]} {credit.account_nr[10:14]} {credit.account_nr[14:18]}"

    return render_template('products_loans.html', credits=credits)


# Wylogowanie
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
