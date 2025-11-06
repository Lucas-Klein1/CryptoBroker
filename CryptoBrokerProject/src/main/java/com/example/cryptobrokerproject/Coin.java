package com.example.cryptobrokerproject;

import javafx.scene.image.Image;
import java.io.ByteArrayInputStream;

public class Coin {
    private final String id;
    private final String symbol;
    private final String name;
    private final byte[] imageData;      // <-- Bilddaten als BLOB (Byte-Array)
    private Image imageObject;     // <-- tatsächliches Bildobjekt
    private final double current_price;
    private final long market_cap;
    private final int market_cap_rank;
    private final long total_volume;
    private final String last_updated;

    public Coin(String id, String symbol, String name, byte[] imageData,
                double current_price, long market_cap, int market_cap_rank,
                long total_volume, String last_updated) {
        this.id = id;
        this.symbol = symbol;
        this.name = name;
        this.imageData = imageData;
        this.current_price = current_price;
        this.market_cap = market_cap;
        this.market_cap_rank = market_cap_rank;
        this.total_volume = total_volume;
        this.last_updated = last_updated;

        // Falls Bilddaten vorhanden, JavaFX Image daraus erzeugen
        try {
            if (imageData != null && imageData.length > 0) {
                this.imageObject = new Image(new ByteArrayInputStream(imageData), 32, 32, true, true);
            }
        } catch (Exception e) {
            this.imageObject = null;
        }
    }

    // === Getter ===
    public String getId() { return id; }
    public String getSymbol() { return symbol; }
    public String getName() { return name; }
    public byte[] getImageData() { return imageData; }      // <-- Zugriff auf die rohen Bytes
    public Image getImageObject() { return imageObject; }   // <-- Für ImageView nutzbar
    public double getCurrent_price() { return current_price; }
    public long getMarket_cap() { return market_cap; }
    public int getMarket_cap_rank() { return market_cap_rank; }
    public long getTotal_volume() { return total_volume; }
    public String getLast_updated() { return last_updated; }
}
