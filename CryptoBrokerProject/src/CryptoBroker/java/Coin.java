public class Coin {
    private String name;
    private int id;
    private byte[] imageData;

    public Coin(String name, int id, byte[] imageData) {
        this.name = name;
        this.id = id;
        this.imageData = imageData;
    }

    public void coin() {

    }

    public String getName() {
        return name;
    }

    public int getId() {
        return id;
    }

    public byte[] getImageData() {
        return imageData;
    }
}
