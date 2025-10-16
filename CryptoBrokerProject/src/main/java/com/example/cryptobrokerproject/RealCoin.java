package com.example.cryptobrokerproject;

import javafx.scene.image.Image;

import java.io.ByteArrayInputStream;

public class RealCoin {
    private String name;
    private byte[] imageData;      // <-- Bilddaten als BLOB (Byte-Array)
    private Image imageObject;     // <-- tatsächliches Bildobjekt
    private double current_price;
    private int market_cap_rank;

    public RealCoin(String name, byte[] imageData, double current_price, int market_cap_rank) {
        this.name = name;
        this.imageData = imageData;
        this.current_price = current_price;
        this.market_cap_rank = market_cap_rank;

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
    public String getName() { return name; }
    public byte[] getImageData() { return imageData; }      // <-- Zugriff auf die rohen Bytes
    public Image getImageObject() { return imageObject; }   // <-- Für ImageView nutzbar
    public double getCurrent_price() { return current_price; }
    public int getMarket_cap_rank() { return market_cap_rank; }
}
