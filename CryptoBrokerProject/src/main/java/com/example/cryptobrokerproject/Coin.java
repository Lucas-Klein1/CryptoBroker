package com.example.cryptobrokerproject;

import javafx.scene.image.Image;

public class Coin {
    private String id;
    private String symbol;
    private String name;
    private String imageUrl;
    private Image imageObject; // <-- tatsächliches Bildobjekt
    private double current_price;
    private long market_cap;
    private int market_cap_rank;
    private long total_volume;
    private String last_updated;

    public Coin(String id, String symbol, String name, String imageUrl,
                double current_price, long market_cap, int market_cap_rank,
                long total_volume, String last_updated) {
        this.id = id;
        this.symbol = symbol;
        this.name = name;
        this.imageUrl = imageUrl;
        this.current_price = current_price;
        this.market_cap = market_cap;
        this.market_cap_rank = market_cap_rank;
        this.total_volume = total_volume;
        this.last_updated = last_updated;

        // Bild nur EINMAL beim Erstellen laden
        try {
            if (imageUrl != null && !imageUrl.isEmpty()) {
                this.imageObject = new Image(imageUrl, 32, 32, true, true);
            }
        } catch (Exception e) {
            this.imageObject = null;
        }
    }

    public String getId() { return id; }
    public String getSymbol() { return symbol; }
    public String getName() { return name; }
    public String getImageUrl() { return imageUrl; }
    public Image getImageObject() { return imageObject; }
    public double getCurrent_price() { return current_price; }
    public long getMarket_cap() { return market_cap; }
    public int getMarket_cap_rank() { return market_cap_rank; }
    public long getTotal_volume() { return total_volume; }
    public String getLast_updated() { return last_updated; }
}

