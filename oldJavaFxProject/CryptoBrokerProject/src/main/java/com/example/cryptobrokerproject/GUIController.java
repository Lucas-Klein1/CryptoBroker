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
import javafx.util.StringConverter;

import javax.swing.*;
import java.io.ByteArrayInputStream;
import java.net.URL;
import java.sql.Timestamp;
import java.sql.Date;
import java.text.NumberFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

public class GUIController implements Initializable {

    private final ObservableList<Coin> coins = FXCollections.observableArrayList();
    private final DBController dbCon = new DBController("jdbc:sqlite:src/main/db/crypto.db");
    private final AccController accCon = new AccController();

    @FXML private GridPane accountPane;
    @FXML private Label cryptLabel;
    @FXML private GridPane cryptPane;
    @FXML private Button accountButton;
    @FXML private Button logoutButton;
    @FXML private GridPane homePane;
    @FXML private GridPane overallPane;
    @FXML private PasswordField passwordField;
    @FXML private LineChart<Number, Number> cryptLineChart;
    @FXML private RadioButton showPassword;
    @FXML private TextField usernameField;
    @FXML private TableColumn<Coin, byte[]> logo;
    @FXML private TableColumn<Coin, String> name;
    @FXML private TableColumn<Coin, Float> price;
    @FXML private TableColumn<Coin, Integer> rank;
    @FXML private TableView<Coin> overviewTable;
    @FXML private TextField showedPassword;
    @FXML private Button registerButton;
    @FXML private PasswordField passwordFieldRegister1;
    @FXML private PasswordField passwordFieldRegister2;
    @FXML private GridPane registerPane;

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

        Account acc = accCon.login(usernameField.getText(), passwordField.getText());

        /*if (usernameField.getText().isEmpty() || passwordField.getText().isEmpty()) {
            JOptionPane.showMessageDialog(null, "Bitte Benutzername und Passwort eingeben.");
            return;
        }
        if (usernameField.getText().length() < 3) {
            JOptionPane.showMessageDialog(null, "Benutzername ist zu kurz.");
            return;
        }
        if (usernameField.getText().contains(" ")) {
            JOptionPane.showMessageDialog(null, "Benutzername darf keine Leerzeichen enthalten.");
            return;
        }
        if (showPassword.isSelected() && showedPassword.getText().length() <= 6
                || !showPassword.isSelected() && passwordField.getText().length() <= 6) {
            JOptionPane.showMessageDialog(null, "Passwort ist zu kurz.");
            return;
        }*/

        if (acc != null) {
            logoutButton.setVisible(true);
            accountButton.setVisible(false);
            accountPane.setVisible(false);
            homePane.setVisible(true);
            cryptPane.setVisible(false);
            passwordField.clear();
            showedPassword.clear();
            usernameField.clear();
        }
    }

    @FXML
    void registerButtonAction(javafx.event.ActionEvent event) {
        System.out.println("registerButtonAction");
    }

    public void showPasswordButton(javafx.event.ActionEvent actionEvent) {
        if (showPassword.isSelected()) {
            showedPassword.setText(passwordField.getText());
            showedPassword.setVisible(true);
            passwordField.setVisible(false);
        } else {
            passwordField.setText(showedPassword.getText());
            showedPassword.setVisible(false);
            passwordField.setVisible(true);
        }
    }

    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        name.setCellValueFactory(new PropertyValueFactory<>("name"));
        price.setCellValueFactory(new PropertyValueFactory<>("current_price"));
        rank.setCellValueFactory(new PropertyValueFactory<>("market_cap_rank"));
        logo.setCellValueFactory(new PropertyValueFactory<>("imageData"));

        logo.setCellFactory(column -> new TableCell<>() {
            private final ImageView imageView = new ImageView();
            {
                imageView.setFitHeight(30);
                imageView.setFitWidth(30);
                imageView.setPreserveRatio(true);
                setContentDisplay(ContentDisplay.GRAPHIC_ONLY);
            }

            @Override
            protected void updateItem(byte[] item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setGraphic(null);
                } else {
                    try (ByteArrayInputStream bis = new ByteArrayInputStream(item)) {
                        imageView.setImage(new Image(bis));
                        setGraphic(imageView);
                    } catch (Exception e) {
                        System.err.println("Fehler beim Laden des Bildes: " + e.getMessage());
                        setGraphic(null);
                    }
                }
            }
        });

        coins.setAll(dbCon.getCoins());
        overviewTable.setItems(coins);
    }

    public void getCryptoData(MouseEvent mouseEvent) {
        Coin coin = overviewTable.getSelectionModel().getSelectedItem();
        if (coin == null) return;

        overallPane.setVisible(false);
        cryptPane.setVisible(true);
        cryptLabel.setText(coin.getName());

        XYChart.Series<Number, Number> series = new XYChart.Series<>();
        series.setName("Preisverlauf – " + coin.getName());

        // 🔹 Neuer DBController-Aufruf statt direkter SQL
        HashMap<Timestamp, Double> history = dbCon.getCoinHistory(coin);

        if (history == null || history.isEmpty()) {
            new Alert(Alert.AlertType.INFORMATION, "Keine Preisdaten für " + coin.getName() + " gefunden.").showAndWait();
            return;
        }

        // Sortieren nach Timestamp
        List<Map.Entry<Timestamp, Double>> sorted = new ArrayList<>(history.entrySet());
        sorted.sort(Comparator.comparing(Map.Entry::getKey));

        List<Double> prices = new ArrayList<>();
        for (Map.Entry<Timestamp, Double> entry : sorted) {
            prices.add(entry.getValue());
        }

        Timestamp minTs = sorted.get(0).getKey();
        double minPrice = Collections.min(prices);
        double maxPrice = Collections.max(prices);

        for (Map.Entry<Timestamp, Double> entry : sorted) {
            long diff = entry.getKey().getTime() - minTs.getTime();
            series.getData().add(new XYChart.Data<>(diff, entry.getValue()));
        }

        cryptLineChart.getData().setAll(series);
        NumberAxis xAxis = (NumberAxis) cryptLineChart.getXAxis();
        NumberAxis yAxis = (NumberAxis) cryptLineChart.getYAxis();

        xAxis.setLabel("Zeit");
        yAxis.setLabel("Preis (EUR)");

        double range = maxPrice - minPrice;
        double padding = range * 0.10;
        if (padding == 0) padding = maxPrice * 0.01;
        yAxis.setAutoRanging(false);
        yAxis.setLowerBound(minPrice - padding);
        yAxis.setUpperBound(maxPrice + padding);
        yAxis.setTickUnit((yAxis.getUpperBound() - yAxis.getLowerBound()) / 5);

        SimpleDateFormat sdf = new SimpleDateFormat("dd.MM HH:mm");
        xAxis.setTickLabelFormatter(new StringConverter<>() {
            @Override
            public String toString(Number value) {
                return sdf.format(new Date(minTs.getTime() + value.longValue()));
            }
            @Override public Number fromString(String s) { return 0; }
        });

        NumberFormat eurFormat = NumberFormat.getCurrencyInstance(Locale.GERMANY);
        yAxis.setTickLabelFormatter(new StringConverter<>() {
            @Override
            public String toString(Number value) {
                return eurFormat.format(value.doubleValue());
            }
            @Override public Number fromString(String s) {
                try { return eurFormat.parse(s).doubleValue(); }
                catch (ParseException e) { return 0; }
            }
        });

        cryptLineChart.setAnimated(false);
        cryptLineChart.setCreateSymbols(false);
        cryptLineChart.setLegendVisible(true);
        cryptLineChart.setTitle("Preisverlauf von " + coin.getName());
        cryptLineChart.setStyle("-fx-background-color: #f9fafb; -fx-border-color: #dee2e6;");

        double firstPrice = prices.get(0);
        double lastPrice = prices.get(prices.size() - 1);
        boolean isUp = lastPrice > firstPrice;

        Platform.runLater(() -> {
            String lineColor = isUp ? "#28a745" : "#dc3545";
            Node line = series.getNode().lookup(".chart-series-line");
            if (line != null) line.setStyle("-fx-stroke: " + lineColor + "; -fx-stroke-width: 2.5px;");
        });
    }
}
