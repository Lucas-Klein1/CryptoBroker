package com.example.cryptobrokerproject;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Label;
import javafx.scene.control.TableCell;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.io.ByteArrayInputStream;
import java.net.URL;
import java.sql.*;
import java.util.ResourceBundle;

public class HelloController implements Initializable {
    private final String DB_URL = "jdbc:sqlite:src/main/db/crypto.db";

    ObservableList<RealCoin> coins = FXCollections.observableArrayList();

    @FXML
    private TableColumn<RealCoin, byte[]> logo;

    @FXML
    private TableColumn<RealCoin, String> name;

    @FXML
    private TableColumn<RealCoin, Float> price;

    @FXML
    private TableColumn<RealCoin, Integer> rank;

    @FXML
    private TableView<RealCoin> overviewTable;


    public void homeButton(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(false);
    }

    public void overAllButton(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(true);
    }

    public static ObservableList<RealCoin> getCoins() {
        ObservableList<RealCoin> list = FXCollections.observableArrayList();
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:src/main/db/crypto.db")){

            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM coins");
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                byte[] imageData = rs.getBytes("image"); // <-- Bild aus BLOB-Feld holen
                list.add(new RealCoin(
                        rs.getString("name"),
                        imageData, // <-- byte[] statt URL
                        rs.getDouble("current_price"),
                        rs.getInt("market_cap_rank")
                ));
            }
            JOptionPane.showMessageDialog(null, "Datenbankverbindung erfolgreich!");
        }catch (Exception e){
            JOptionPane.showMessageDialog(null, e);
        }
        return list;
    }


    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        name.setCellValueFactory(new PropertyValueFactory<RealCoin, String>("name"));
        price.setCellValueFactory(new PropertyValueFactory<RealCoin, Float>("current_price"));
        rank.setCellValueFactory(new PropertyValueFactory<RealCoin, Integer>("market_cap_rank"));
        logo.setCellValueFactory(new PropertyValueFactory<RealCoin, byte[]>("imageData")); // imageData ist das byte[] Feld in RealCoin
        logo.setCellFactory(column -> {
            return new TableCell<RealCoin, byte[]>() { // Der Typ des Items in dieser Zelle ist byte[]
                private final ImageView imageView = new ImageView();

                {
                    // Optional: Größe des Bildes festlegen, damit es in die Zelle passt
                    imageView.setFitHeight(30); // Oder eine andere passende Größe
                    imageView.setFitWidth(30);
                    imageView.setPreserveRatio(true); // Wichtig, um das Seitenverhältnis zu erhalten

                    // Setze den ImageView als Grafik für die Zelle
                    // setGraphic(imageView); // Dies wird in updateItem gemacht, um leere Zellen zu handhaben
                    setContentDisplay(javafx.scene.control.ContentDisplay.GRAPHIC_ONLY); // Zeigt nur das Bild, keinen Text
                }

                @Override
                protected void updateItem(byte[] item, boolean empty) {
                    super.updateItem(item, empty);

                    if (empty || item == null) {
                        // Wenn die Zelle leer ist oder kein Bilddaten vorhanden sind,
                        // zeige nichts an. Wichtig: setGraphic(null) entfernt alte Grafiken.
                        imageView.setImage(null);
                        setGraphic(null);
                    } else {
                        // Wenn Bilddaten vorhanden sind, erstelle ein Image aus dem byte[]
                        // und setze es in den ImageView.
                        try (ByteArrayInputStream bis = new ByteArrayInputStream(item)) {
                            Image image = new Image(bis);
                            imageView.setImage(image);
                            setGraphic(imageView); // Setze den ImageView als Grafik für die Zelle
                        } catch (Exception e) {
                            // Fehlerbehandlung, falls das byte[] keine gültigen Bilddaten enthält
                            System.err.println("Fehler beim Laden des Bildes aus Byte-Array: " + e.getMessage());
                            imageView.setImage(null);
                            setGraphic(null);
                        }
                    }
                }
            };
        });

        coins = getCoins();
        System.out.println(coins);
        overviewTable.setItems(coins);
    }
}