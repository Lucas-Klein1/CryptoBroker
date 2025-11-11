package com.example.cryptobrokerproject;

import javafx.scene.image.Image;

import java.io.ByteArrayInputStream;

public class OldRealCoin {
    private String name;
    private String id;
    private byte[] imageData;      // <-- Bilddaten als BLOB (Byte-Array)
    private Image imageObject;     // <-- tatsächliches Bildobjekt
    private double current_price;
    private int market_cap_rank;

    public OldRealCoin(String id, String name, byte[] imageData, double current_price, int market_cap_rank) {
        this.id = id;
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
    public byte[] getImageData() { return imageData; }          // <-- Zugriff auf die rohen Bytes
    public Image getImageObject() { return imageObject; }       // <-- Für ImageView nutzbar
    public double getCurrent_price() { return current_price; }
    public int getMarket_cap_rank() { return market_cap_rank; }

    public void setName(String name) {
        this.name = name;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setImageData(byte[] imageData) {
        this.imageData = imageData;
    }

    public void setImageObject(Image imageObject) {
        this.imageObject = imageObject;
    }

    public void setCurrent_price(double current_price) {
        this.current_price = current_price;
    }

    public void setMarket_cap_rank(int market_cap_rank) {
        this.market_cap_rank = market_cap_rank;
    }

    @Override
    public String toString() {
        return "RealCoin{" +
                "name='" + name + '\'' + "imgeData='" + imageData + '\'' +
                ", current_price=" + current_price +
                ", market_cap_rank=" + market_cap_rank +
                '}'  + "\n" ;
    }
}