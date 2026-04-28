from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.account import Account
from models.coin import Coin
from models.favorite import Favorite
from services.portfolio_service import PortfolioService
from services.market_service import MarketService
from services.coin_sync_service import CoinSyncService

app = Flask(__name__)
app.secret_key = "change-me-in-production"  # für Sessions & flash

portfolio_service = PortfolioService()
market_service = MarketService()

coin_sync_service = CoinSyncService()

# Tabelle beim Start aktualisieren
coin_sync_service.update_coins_table()

# ---------- EURO FORMAT FILTER ----------
@app.template_filter("eur")
def eur_format(value):
    try:
        return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return value
# ----------------------------------------

@app.template_filter("datetimeformat")
def datetimeformat(value):
    import datetime
    return datetime.datetime.fromtimestamp(value / 1000).strftime("%d.%m.%Y %H:%M")



@app.route("/")
def home():
    acc_id = session.get("acc_id")
    favorites = Favorite.get_for_account(acc_id) if acc_id else []
    return render_template("home.html", favorites=favorites)


@app.route("/dashboard")
def dashboard():
    coins = market_service.get_all_coins()
    return render_template("dashboard.html", coins=coins)


@app.route("/portfolio")
def portfolio():
    acc_id = session.get("acc_id")
    if not acc_id:
        flash("Bitte melde dich zuerst an.", "error")
        return redirect(url_for("profile"))

    positions, total_value = portfolio_service.get_portfolio_overview(acc_id)
    balance = market_service.get_balance(acc_id)
    portfolio_history = market_service.get_portfolio_history(acc_id)
    return render_template("portfolio.html", positions=positions, total_value=total_value,
                           balance=balance, portfolio_history=portfolio_history)


@app.route("/transactions")
def transactions():
    acc_id = session.get("acc_id")
    if not acc_id:
        flash("Bitte melde dich zuerst an.", "error")
        return redirect(url_for("profile"))

    txs = market_service.get_transactions(acc_id)
    return render_template("transactions.html", txs=txs)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        name = request.form.get("name")
        pw = request.form.get("pw")
        try:
            account = Account.login_or_register(name, pw)
            session["acc_id"] = account.id
            flash(f"Willkommen, {account.name}!", "success")
            return redirect(url_for("dashboard"))
        except ValueError as e:
            flash(str(e), "error")

    acc_id = session.get("acc_id")
    account = Account.get_by_id(acc_id) if acc_id else None
    return render_template("profile.html", account=account)


@app.route("/logout")
def logout():
    session.clear()
    flash("Du wurdest erfolgreich abgemeldet.", "success")
    return redirect(url_for("home"))


@app.route("/change-password", methods=["POST"])
def change_password():
    acc_id = session.get("acc_id")
    if not acc_id:
        flash("Bitte melde dich zuerst an.", "error")
        return redirect(url_for("profile"))

    account = Account.get_by_id(acc_id)
    old_pw = request.form.get("old_pw")
    new_pw = request.form.get("new_pw")
    confirm_pw = request.form.get("confirm_pw")

    if new_pw != confirm_pw:
        flash("Neues Passwort und Bestätigung stimmen nicht überein.", "error")
        return redirect(url_for("profile"))

    try:
        account.change_password(old_pw, new_pw)
        flash("Passwort erfolgreich geändert.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("profile"))


@app.route("/coin/<coin_id>")
def coin_detail(coin_id):
    coin = Coin.get_by_id(coin_id)
    if coin is None:
        flash("Coin nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    # Synchronisiere History für diesen Coin
    coin_sync_service.sync_coin_history(coin_id, days=365)

    history = market_service.get_history(coin_id)

    acc_id = session.get("acc_id")
    position = None
    balance = None
    is_favorite = False
    if acc_id:
        position = market_service.get_position(acc_id, coin_id)
        balance = market_service.get_balance(acc_id)
        is_favorite = Favorite.is_favorite(acc_id, coin_id)

    return render_template("coin_detail.html", coin=coin, history=history,
                           position=position, balance=balance,
                           is_favorite=is_favorite)


@app.route("/favorite/<coin_id>/toggle", methods=["POST"])
def toggle_favorite(coin_id):
    acc_id = session.get("acc_id")
    if not acc_id:
        flash("Bitte melde dich zuerst an, um Favoriten zu speichern.", "error")
        return redirect(url_for("profile"))

    coin = Coin.get_by_id(coin_id)
    if coin is None:
        flash("Coin nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    now_favorite = Favorite.toggle(acc_id, coin_id)
    if now_favorite:
        flash(f"{coin.name} zu deinen Favoriten hinzugefügt.", "success")
    else:
        flash(f"{coin.name} aus deinen Favoriten entfernt.", "success")

    return redirect(url_for("coin_detail", coin_id=coin_id))


@app.route("/trade/<coin_id>", methods=["POST"])
def trade(coin_id):
    acc_id = session.get("acc_id")
    if not acc_id:
        flash("Bitte melde dich zuerst an.", "error")
        return redirect(url_for("profile"))

    action = (request.form.get("action") or "").upper()
    raw_amount = request.form.get("amount") or "0"

    try:
        amount = float(raw_amount.replace(",", "."))
    except ValueError:
        flash("Ungültige Menge.", "error")
        return redirect(url_for("coin_detail", coin_id=coin_id))

    if amount <= 0:
        flash("Menge muss größer als 0 sein.", "error")
        return redirect(url_for("coin_detail", coin_id=coin_id))

    coin = Coin.get_by_id(coin_id)
    if coin is None:
        flash("Coin nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    try:
        market_service.execute_trade(acc_id, coin_id, action, amount)
    except ValueError as e:
        flash(str(e), "error")
    else:
        if action == "BUY":
            flash(f"Erfolgreich {amount} {coin.symbol.upper()} gekauft.", "success")
        elif action == "SELL":
            flash(f"Erfolgreich {amount} {coin.symbol.upper()} verkauft.", "success")
        else:
            flash("Unbekannte Aktion.", "error")

    return redirect(url_for("coin_detail", coin_id=coin_id))



if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
