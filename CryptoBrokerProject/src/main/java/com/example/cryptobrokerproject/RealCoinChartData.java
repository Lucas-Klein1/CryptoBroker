package com.example.cryptobrokerproject;

public class RealCoinChartData {
    private int timeStamp_ms;
    private double price;
    private double marketCap;
    private double volume;

    public RealCoinChartData(int timeStamp_ms, double price, double marketCap, double volume) {
        this.timeStamp_ms = timeStamp_ms;
        this.price = price;
        this.marketCap = marketCap;
        this.volume = volume;
    }

    public int getTimeStamp_ms() {
        return timeStamp_ms;
    }

    public void setTimeStamp_ms(int timeStamp_ms) {
        this.timeStamp_ms = timeStamp_ms;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public double getMarketCap() {
        return marketCap;
    }

    public void setMarketCap(double marketCap) {
        this.marketCap = marketCap;
    }

    public double getVolume() {
        return volume;
    }

    public void setVolume(double volume) {
        this.volume = volume;
    }
}
