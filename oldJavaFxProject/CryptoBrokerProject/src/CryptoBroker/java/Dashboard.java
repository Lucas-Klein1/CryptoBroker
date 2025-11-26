import javafx.scene.control.TableView;

public class Dashboard {
    private TableView<Coin> tableView;

    public Dashboard(TableView<Coin> tableView) {
        this.tableView = tableView;
    }

    public void initialize() {
        // Initialisierungscode für das Dashboard
    }

    public void showCoins (){
        // Code zum Setzen der Coins in die TableView
    }

    public void loadCoinsFromDB(){
        // Code zum Laden der Coins aus der Datenbank
    }

}
