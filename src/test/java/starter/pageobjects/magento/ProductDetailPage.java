package starter.pageobjects.magento;

import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

public class ProductDetailPage extends PageObject {

    public static final By PRODUCT_NAME = By.cssSelector(".page-title span.base");
    public static final By PRICE = By.cssSelector(".product-info-price .price");
    public static final By ADD_TO_CART = By.id("product-addtocart-button");

    public String productName() {
        return $(PRODUCT_NAME).waitUntilVisible().getText();
    }

    public String price() {
        return $(PRICE).waitUntilVisible().getText();
    }

    public boolean addToCartIsAvailable() {
        return $(ADD_TO_CART).isCurrentlyVisible();
    }
}
