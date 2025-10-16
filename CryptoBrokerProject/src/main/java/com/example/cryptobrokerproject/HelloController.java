package com.example.cryptobrokerproject;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.control.TableView;

import java.awt.event.ActionEvent;
import java.sql.*;

public class HelloController {
    private final String DB_URL = "jdbc:sqlite:src/main/db/crypto.db";

    ObservableList<RealCoin> coins = FXCollections.observableArrayList();

    @FXML
    private Label welcomeText;

    @FXML
    private TableView overviewTable;

    @FXML
    protected void onHelloButtonClick() {
        welcomeText.setText("Welcome to JavaFX Application!");
    }

    public void homeButton(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(false);
    }

    public void overAllButton(javafx.event.ActionEvent actionEvent) {
        coins.clear();
        loadCoinsFromDB(coins);
        overviewTable.setItems(coins);
        overviewTable.setVisible(true);
    }

    private void loadCoinsFromDB(ObservableList<RealCoin> coins) {
        try (Connection conn = DriverManager.getConnection(DB_URL)) {
            String sql = "SELECT * FROM coins";
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql);

            while (rs.next()) {
                byte[] imageData = rs.getBytes("image"); // <-- Bild aus BLOB-Feld holen

                coins.add(new RealCoin(
                        rs.getString("name"),
                        imageData, // <-- byte[] statt URL
                        rs.getDouble("current_price"),
                        rs.getInt("market_cap_rank")
                ));
                System.out.println(coins);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }


}