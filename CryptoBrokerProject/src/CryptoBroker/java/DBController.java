import javafx.collections.ObservableList;

import java.sql.Connection;

public class DBController {
    private Connection dBConnection;

    public DBController(Connection dBConnection) {
        this.dBConnection = dBConnection;
    }

    public void connectToDB() {
        // Code to connect to the database
    }

    public Account getAccount(int accountId) {
        // Code to retrieve account details from the database
        return null;
    }

    public ObservableList<Coin> getCoinList() {
        return null;
    }

    public void getCoinHistory(Coin coin) {
        // Code to retrieve coin history from the database
    }
}
