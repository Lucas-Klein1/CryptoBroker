package com.example.cryptobrokerproject;

import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.text.Font;
import javafx.util.StringConverter;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.io.ByteArrayInputStream;
import java.net.URL;
import java.sql.*;
import java.sql.Date;
import java.text.NumberFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

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

    public void getCryptoData(MouseEvent mouseEvent) {
        RealCoin coin = overviewTable.getSelectionModel().getSelectedItem();
        if (coin == null) return;

        overallPane.setVisible(false);
        cryptPane.setVisible(true);
        cryptLabel.setText(coin.getName());

        String tableName = coin.getId().replace("-", "_") + "_history";
        XYChart.Series<Number, Number> series = new XYChart.Series<>();
        series.setName("Preisverlauf – " + coin.getName());

        List<Long> timestamps = new ArrayList<>();
        List<Double> prices = new ArrayList<>();

        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement stmt = conn.prepareStatement("SELECT timestamp_ms, price FROM " + tableName);
             ResultSet rs = stmt.executeQuery()) {

            while (rs.next()) {
                timestamps.add(rs.getLong("timestamp_ms"));
                prices.add(rs.getDouble("price"));
            }

        } catch (SQLException e) {
            new Alert(Alert.AlertType.ERROR, "Fehler beim Laden der Kursdaten:\n" + e.getMessage()).showAndWait();
            return;
        }

        if (timestamps.isEmpty()) return;

        long minTs = Collections.min(timestamps);
        long maxTs = Collections.max(timestamps);
        double minPrice = Collections.min(prices);
        double maxPrice = Collections.max(prices);

        // === Daten in Serie einfügen ===
        for (int i = 0; i < timestamps.size(); i++) {
            series.getData().add(new XYChart.Data<>(timestamps.get(i) - minTs, prices.get(i)));
        }

        cryptLineChart.getData().clear();
        cryptLineChart.getData().add(series);

        NumberAxis xAxis = (NumberAxis) cryptLineChart.getXAxis();
        NumberAxis yAxis = (NumberAxis) cryptLineChart.getYAxis();

        xAxis.setLabel("Zeit");
        yAxis.setLabel("Preis (EUR)");

        // === Y-Achse: 10 % Puffer ===
        double range = maxPrice - minPrice;
        double padding = range * 0.10;
        if (padding == 0) padding = maxPrice * 0.01;
        yAxis.setAutoRanging(false);
        yAxis.setLowerBound(minPrice - padding);
        yAxis.setUpperBound(maxPrice + padding);
        yAxis.setTickUnit((yAxis.getUpperBound() - yAxis.getLowerBound()) / 5);

        // === Zeit-Achse (dd.MM HH:mm) ===
        SimpleDateFormat sdf = new SimpleDateFormat("dd.MM HH:mm");
        xAxis.setTickLabelFormatter(new StringConverter<Number>() {
            @Override
            public String toString(Number value) {
                return sdf.format(new Date(minTs + value.longValue()));
            }

            @Override
            public Number fromString(String string) {
                return 0;
            }
        });

        // === EUR-Formatierung der Preisachse ===
        NumberFormat eurFormat = NumberFormat.getCurrencyInstance(Locale.GERMANY);
        eurFormat.setMaximumFractionDigits(2);
        eurFormat.setMinimumFractionDigits(2);

        yAxis.setTickLabelFormatter(new StringConverter<Number>() {
            @Override
            public String toString(Number value) {
                return eurFormat.format(value.doubleValue());
            }

            @Override
            public Number fromString(String string) {
                try {
                    return eurFormat.parse(string).doubleValue();
                } catch (ParseException e) {
                    return 0;
                }
            }
        });

        // === Chart-Styling ===
        cryptLineChart.setAnimated(false);
        cryptLineChart.setCreateSymbols(false);
        cryptLineChart.setLegendVisible(true);
        cryptLineChart.setTitle("Preisverlauf von " + coin.getName());
        cryptLineChart.setVerticalGridLinesVisible(true);
        cryptLineChart.setHorizontalGridLinesVisible(true);
        cryptLineChart.setStyle("-fx-background-color: #f9fafb; -fx-border-color: #dee2e6;");

        // === Farbwahl (grün/rot) ===
        double firstPrice = prices.get(0);
        double lastPrice = prices.get(prices.size() - 1);
        boolean isUp = lastPrice > firstPrice;

        Platform.runLater(() -> {
            String lineColor = isUp ? "#28a745" : "#dc3545"; // grün oder rot
            Node line = series.getNode().lookup(".chart-series-line");
            if (line != null) {
                line.setStyle("-fx-stroke: " + lineColor + "; -fx-stroke-width: 2.5px;");
            }
        });
    }
}