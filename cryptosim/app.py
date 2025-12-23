from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.account import Account
from models.coin import Coin
from services.portfolio_service import PortfolioService
from services.market_service import MarketService

app = Flask(__name__)
app.secret_key = "change-me-in-production"  # für Sessions & flash

portfolio_service = PortfolioService()
market_service = MarketService()


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
    return render_template("home.html")


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
    return render_template("portfolio.html", positions=positions, total_value=total_value)

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


@app.route("/coin/<coin_id>")
def coin_detail(coin_id):
    coin = Coin.get_by_id(coin_id)
    if coin is None:
        flash("Coin nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    history = market_service.get_history(coin_id)

    acc_id = session.get("acc_id")
    position = None
    if acc_id:
        position = market_service.get_position(acc_id, coin_id)

    return render_template("coin_detail.html", coin=coin, history=history, position=position)


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

@app.route("/coin_image/<coin_id>")
def coin_image(coin_id):
    from models.database import Database

    conn = Database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT image FROM coins WHERE id = ?", (coin_id,))
    row = cur.fetchone()
    conn.close()

    if row is None or row["image"] is None:
        # Fallback: leeres Pixel-PNG
        empty_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc``\x00\x00\x00\x02\x00\x01'
            b'\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        return empty_png, 200, {"Content-Type": "image/png"}

    img_bytes = row["image"]
    return img_bytes, 200, {"Content-Type": "image/png"}



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
