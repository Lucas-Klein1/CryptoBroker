package com.example.cryptobrokerproject;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.XYChart;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.GridPane;

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
    private GridPane accountPane;

    @FXML
    private Label cryptLabel;

    @FXML
    private GridPane cryptPane;

    @FXML
    private Button accountButton;

    @FXML
    private Button logoutButton;

    @FXML
    private GridPane homePane;

    @FXML
    private GridPane overallPane;

    @FXML
    private PasswordField passwordField;

    @FXML
    private LineChart<Number, Number> cryptLineChart;

    @FXML
    private RadioButton showPassword;

    @FXML
    private TextField usernameField;

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

    @FXML
    private TextField showedPassword;

    public void homeButtonAction(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(false);
        homePane.setVisible(true);
        accountPane.setVisible(false);
        overallPane.setVisible(false);
        cryptPane.setVisible(false);
    }

    public void overAllButtonAction(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(true);
        homePane.setVisible(false);
        accountPane.setVisible(false);
        overallPane.setVisible(true);
        cryptPane.setVisible(false);
    }

    public void accountButtonAction(javafx.event.ActionEvent actionEvent) {
        overviewTable.setVisible(false);
        homePane.setVisible(false);
        accountPane.setVisible(true);
        overallPane.setVisible(false);
        cryptPane.setVisible(false);
    }

    public void logoutButtonAction(javafx.event.ActionEvent actionEvent) {
        logoutButton.setVisible(false);
        cryptPane.setVisible(false);
        accountButton.setVisible(true);
        homePane.setVisible(true);
        overallPane.setVisible(false);
        accountPane.setVisible(false);
        JOptionPane.showMessageDialog(null, "Erfolgreich ausgeloggt.");
    }

    public void loginButtonAction(javafx.event.ActionEvent actionEvent) {
        if (usernameField.getText().isEmpty() || passwordField.getText().isEmpty()) {
            JOptionPane.showMessageDialog(null, "Bitte Benutzername und Passwort eingeben.");
            return;
        }
        if (usernameField.getText().length() < 3) {
            JOptionPane.showMessageDialog(null, "Benutzername ist zu kurz.");
            return;
        }
        String[] parts = usernameField.getText().split(" ");
        if (parts.length > 1) {
            JOptionPane.showMessageDialog(null, "Benutzername darf keine Leerzeichen enthalten.");
            return;
        }
        if (showPassword.isSelected() && 6 >= showedPassword.getText().length()) {
            JOptionPane.showMessageDialog(null, "Passwort ist zu kurz.");
            return;
        }else if (!showPassword.isSelected() && 6 >= passwordField.getText().length()) {
            JOptionPane.showMessageDialog(null, "Passwort ist zu kurz.");
            return;
        }
        logoutButton.setVisible(true);
        accountButton.setVisible(false);
        accountPane.setVisible(false);
        homePane.setVisible(true);
        cryptPane.setVisible(false);
        passwordField.setText("");
        showedPassword.setText("");
        usernameField.setText("");
    }

    public void showPasswordButton(javafx.event.ActionEvent actionEvent) {
        if (showPassword.isSelected()) {
            showedPassword.setText(passwordField.getText());
            showedPassword.setVisible(true);
            passwordField.setVisible(false);
        }else {
            passwordField.setText(showedPassword.getText());
            showedPassword.setVisible(false);
            passwordField.setVisible(true);
        }
    }

    public static ObservableList<RealCoin> getCoins() {
        ObservableList<RealCoin> list = FXCollections.observableArrayList();
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:src/main/db/crypto.db")){

            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM coins");
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                byte[] imageData = rs.getBytes("image"); // <-- Bild aus BLOB-Feld holen
                list.add(new RealCoin(
                        rs.getString("id"),
                        rs.getString("name"),
                        imageData, // <-- byte[] statt URL
                        rs.getDouble("current_price"),
                        rs.getInt("market_cap_rank")
                ));
            }
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
                        try (   ByteArrayInputStream bis = new ByteArrayInputStream(item)) {
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
        overviewTable.setItems(coins);
    }

    public void getCryptoData(MouseEvent mouseEvent) throws SQLException {
        RealCoin coin = overviewTable.getSelectionModel().getSelectedItem();
        if (coin != null) {
            overallPane.setVisible(false);
            cryptPane.setVisible(true);
            cryptLabel.setText(coin.getName());
            String priceText = coin.getId().replace("-","_")+"_history";
            XYChart.Series series = new XYChart.Series();
            try (Connection conn = DriverManager.getConnection(DB_URL)) {
                PreparedStatement stmt = conn.prepareStatement("SELECT * FROM " + priceText);
                ResultSet rs = stmt.executeQuery();
                series.setName("Preisverlauf von " + coin.getName());
                while (rs.next()) {
                    rs.next();
                    rs.next();
                    System.out.println(new Date(rs.getLong("timestamp_ms")));
                    Number ts = rs.getInt("timestamp_ms");
                    double priceVal = rs.getDouble("price");
                    series.getData().add(new XYChart.Data(ts, priceVal));
                }
                cryptLineChart.getData().clear();
                cryptLineChart.getData().add(series);
                cryptPane.setVisible(true);
            } catch (SQLException e) {
                JOptionPane.showMessageDialog(null, e);
            }
        }
    }
}