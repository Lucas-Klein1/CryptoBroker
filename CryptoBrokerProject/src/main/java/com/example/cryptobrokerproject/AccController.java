package com.example.cryptobrokerproject;

import javafx.scene.control.Alert;

public class AccController {
    DBController DB_con = new DBController("jdbc:sqlite:src/main/db/crypto.db");

    public Account login(String username, String password) {
        Account account;
        if (DB_con.verifyAccount(username, password)>=0) {
            account = new Account(username, DB_con.verifyAccount(username, password));
        }
        else {
            account = null;
        }
        return account;
    }

    public Account register(String username, String password) {
        if (!verify(username, password))
            return null;
        else{
            DB_con.addAccount(username, password);
            return new Account(username, DB_con.verifyAccount(username, password));
        }
    }

    private boolean verify(String username, String password) {
        if (username.isEmpty() || password.isEmpty()) {
            showError("Username or password is empty");
            return false;
        }
        if (username.length() < 5) {
            showError("Username must be at least 5 characters long");
            return false;
        }
        if (password.length() < 8) {
            showError("Password must be at least 8 characters long");
            return false;
        }
        if (username.contains(" ")) {
            showError("Username cannot contain spaces");
            return false;
        }
        if (password.contains(" ")) {
            showError("Password cannot contain spaces");
            return false;
        }
        if (DB_con.isUsernameTaken(username)) {
            showError("Username is already taken");
            return false;
        }
        if (DB_con.verifyAccount(username, password)>=0){
            System.out.println("Account already exists");
            showError("Account already exists");
            return false;
        }
        return true;
    }

    private void showError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("Error");
        alert.setHeaderText("An Error occurred");
        alert.setContentText(message);
        alert.showAndWait();
    }
}
