package com.example.cryptobrokerproject;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;

import javax.swing.*;
import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class DBController {

    private String DB_URL = "jdbc:sqlite:src/main/db/crypto.db";

    public DBController(String dbURL) {
        DB_URL = dbURL;

        if (dbURL == null) {
            JOptionPane.showMessageDialog(null, "Keine Datenbank gefunden.");
        }
    }

    /**
     * Erstellt die Tabellen 'accounts' und 'transactions', falls sie noch nicht existieren.
     */
    public void createAccountAndTransactionTables() {
        String createAccountsTable = """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                pw TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """;

        String createTransactionsTable = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id INTEGER NOT NULL,
                acc_id INTEGER NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN ('BUY','SELL')) DEFAULT 'BUY',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (coin_id) REFERENCES coins(id),
                FOREIGN KEY (acc_id) REFERENCES accounts(id)
            );
        """;

        try (Connection conn = DriverManager.getConnection(DB_URL);
             Statement stmt = conn.createStatement()) {

            stmt.execute(createAccountsTable);
            stmt.execute(createTransactionsTable);
            System.out.println("Account- und Transaction-Tabellen erfolgreich erstellt oder bereits vorhanden.");

        } catch (SQLException e) {
            JOptionPane.showMessageDialog(null, "Fehler beim Erstellen der Tabellen: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Fügt einen neuen Account hinzu.
     */
    public boolean addAccount(String name, String pw) {
        String sql = "INSERT INTO accounts (name, pw) VALUES (?, ?)";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            stmt.setString(2, pw); // Später: Passwort-Hash verwenden!
            stmt.executeUpdate();
            System.out.println("Account erstellt: " + name);
            return true;

        } catch (SQLException e) {
            System.err.println("Fehler beim Erstellen des Accounts: " + e.getMessage());
            return false;
        }
    }

    /**
     * Verifiziert einen Account (Login-Prüfung).
     */
    public boolean verifyAccount(String name, String pw) {
        String sql = "SELECT * FROM accounts WHERE name = ? AND pw = ?";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            stmt.setString(2, pw);
            ResultSet rs = stmt.executeQuery();

            return rs.next(); // true, wenn Account gefunden

        } catch (SQLException e) {
            System.err.println("Fehler bei der Account-Verifizierung: " + e.getMessage());
            return false;
        }
    }

    /**
     * Fügt eine Transaktion hinzu.
     */
    public boolean addTransaction(int coinId, int accId, double price, double amount, String type) {
        String sql = """
            INSERT INTO transactions (coin_id, acc_id, price, amount, type)
            VALUES (?, ?, ?, ?, ?)
        """;
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, coinId);
            stmt.setInt(2, accId);
            stmt.setDouble(3, price);
            stmt.setDouble(4, amount);
            stmt.setString(5, type.toUpperCase());
            stmt.executeUpdate();

            System.out.println("Transaktion hinzugefügt (Account " + accId + "): " + type + " " + amount + " @ " + price);
            return true;

        } catch (SQLException e) {
            System.err.println("Fehler beim Hinzufügen der Transaktion: " + e.getMessage());
            return false;
        }
    }

    /**
     * Gibt alle Transaktionen eines bestimmten Accounts zurück.
     */
    public List<String> getTransactionsByAccount(int accId) {
        List<String> transactions = new ArrayList<>();
        String sql = "SELECT * FROM transactions WHERE acc_id = ? ORDER BY timestamp DESC";

        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, accId);
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                String line = String.format(
                        "[%s] %s %f @ %f (Coin-ID: %d)",
                        rs.getString("timestamp"),
                        rs.getString("type"),
                        rs.getDouble("amount"),
                        rs.getDouble("price"),
                        rs.getInt("coin_id")
                );
                transactions.add(line);
            }

        } catch (SQLException e) {
            System.err.println("Fehler beim Abrufen der Transaktionen: " + e.getMessage());
        }

        return transactions;
    }

    public ObservableList<Coin> getCoins() {
        ObservableList<Coin> list = FXCollections.observableArrayList();
        try (Connection conn = DriverManager.getConnection(DB_URL)) {

            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM coins");
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                byte[] imageData = rs.getBytes("image");

                list.add(new Coin(
                        rs.getString("id"),
                        rs.getString("symbol"),
                        rs.getString("name"),
                        imageData,
                        rs.getDouble("current_price"),
                        rs.getLong("market_cap"),
                        rs.getInt("market_cap_rank"),
                        rs.getLong("total_volume"),
                        rs.getString("last_updated")
                ));
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, e);
        }
        return list;
    }

    public HashMap<Timestamp, Double> getCoinHistory(Coin coin) {
        HashMap<Timestamp, Double> map = new HashMap<>();
        String tableName = coin.getId().replace("-", "_") + "_history";

        try (Connection conn = DriverManager.getConnection(DB_URL)) {
            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM " + tableName);
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                Timestamp timestamp = rs.getTimestamp("timestamp");
                Double price = rs.getDouble("price");
                map.put(timestamp, price);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return map;
    }
}
