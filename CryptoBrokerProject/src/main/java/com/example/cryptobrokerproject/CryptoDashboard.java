package com.example.cryptobrokerproject;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.TableCell;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.BorderPane;
import javafx.stage.Stage;
import org.controlsfx.control.Notifications;
import org.kordamp.bootstrapfx.BootstrapFX;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class CryptoDashboard extends Application {

    private final String DB_URL = "jdbc:sqlite:src/main/db/crypto.db";
    private TableView<Coin> tableView;

    @Override
    public void start(Stage stage) {
        stage.setTitle("Crypto Dashboard");

        tableView = new TableView<>();
        setupTableColumns();

        ObservableList<Coin> coins = FXCollections.observableArrayList();
        loadCoinsFromDB(coins);
        tableView.setItems(coins);

        // Doppelklick zeigt Info über den Coin
        tableView.setOnMouseClicked(event -> {
            if (event.getClickCount() == 2 && tableView.getSelectionModel().getSelectedItem() != null) {
                Coin c = tableView.getSelectionModel().getSelectedItem();
                Notifications.create()
                        .title(c.getName() + " (" + c.getSymbol() + ")")
                        .text("Preis: " + c.getCurrent_price() + " €\n" +
                                "Marktkapitalisierung: " + c.getMarket_cap() + "\n" +
                                "Rang: " + c.getMarket_cap_rank() + "\n" +
                                "Volumen: " + c.getTotal_volume() + "\n" +
                                "Zuletzt aktualisiert: " + c.getLast_updated())
                        .showInformation();
            }
        });

        BorderPane root = new BorderPane(tableView);
        root.setPadding(new Insets(15));

        Scene scene = new Scene(root, 1100, 600);
        scene.getStylesheets().add(BootstrapFX.bootstrapFXStylesheet());

        stage.setScene(scene);
        stage.show();
    }

    /**
     * Erstellt alle Spalten der Tabelle, inklusive Bildspalte.
     */
    private void setupTableColumns() {
        // --- Bildspalte ---
        TableColumn<Coin, Image> imageCol = new TableColumn<>("Logo");
        imageCol.setCellValueFactory(new PropertyValueFactory<>("imageObject"));
        imageCol.setPrefWidth(60);

        imageCol.setCellFactory(col -> new TableCell<>() {
            private final ImageView imageView = new ImageView();

            {
                imageView.setFitHeight(32);
                imageView.setFitWidth(32);
                imageView.setPreserveRatio(true);
            }

            @Override
            protected void updateItem(Image img, boolean empty) {
                super.updateItem(img, empty);
                if (empty || img == null) {
                    setGraphic(null);
                } else {
                    imageView.setImage(img);
                    setGraphic(imageView);
                }
            }
        });

        // --- Weitere Spalten ---
        TableColumn<Coin, String> nameCol = new TableColumn<>("Name");
        nameCol.setCellValueFactory(new PropertyValueFactory<>("name"));
        nameCol.setPrefWidth(160);

        TableColumn<Coin, String> symbolCol = new TableColumn<>("Symbol");
        symbolCol.setCellValueFactory(new PropertyValueFactory<>("symbol"));
        symbolCol.setPrefWidth(100);

        TableColumn<Coin, Double> priceCol = new TableColumn<>("Preis (€)");
        priceCol.setCellValueFactory(new PropertyValueFactory<>("current_price"));
        priceCol.setPrefWidth(120);

        TableColumn<Coin, Long> marketCapCol = new TableColumn<>("Marktkapitalisierung");
        marketCapCol.setCellValueFactory(new PropertyValueFactory<>("market_cap"));
        marketCapCol.setPrefWidth(180);

        TableColumn<Coin, Integer> rankCol = new TableColumn<>("Rang");
        rankCol.setCellValueFactory(new PropertyValueFactory<>("market_cap_rank"));
        rankCol.setPrefWidth(100);

        TableColumn<Coin, Long> volumeCol = new TableColumn<>("Volumen");
        volumeCol.setCellValueFactory(new PropertyValueFactory<>("total_volume"));
        volumeCol.setPrefWidth(160);

        TableColumn<Coin, String> updatedCol = new TableColumn<>("Letztes Update");
        updatedCol.setCellValueFactory(new PropertyValueFactory<>("last_updated"));
        updatedCol.setPrefWidth(180);

        tableView.getColumns().addAll(imageCol, nameCol, symbolCol, priceCol,
                marketCapCol, rankCol, volumeCol, updatedCol);
    }

    /**
     * Lädt alle Coins aus der SQLite-Datenbank.
     */
    private void loadCoinsFromDB(ObservableList<Coin> coins) {
        try (Connection conn = DriverManager.getConnection(DB_URL)) {
            String sql = "SELECT * FROM coins";
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql);

            while (rs.next()) {
                byte[] imageData = rs.getBytes("image"); // <-- Bild aus BLOB-Feld holen

                coins.add(new Coin(
                        rs.getString("id"),
                        rs.getString("symbol"),
                        rs.getString("name"),
                        imageData, // <-- byte[] statt URL
                        rs.getDouble("current_price"),
                        rs.getLong("market_cap"),
                        rs.getInt("market_cap_rank"),
                        rs.getLong("total_volume"),
                        rs.getString("last_updated")
                ));
                System.out.println(coins);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
