package com.example.cryptobrokerproject.main;

public class Account {
    String name;
    int id;

    public Account(String name, int id) {
        this.name = name;
        this.id = id;
    }

    public int getID(){
        return id;
    }

    public String getName(){
        return name;
    }
}
