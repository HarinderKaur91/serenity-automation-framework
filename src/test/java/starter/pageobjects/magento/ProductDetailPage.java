package starter.pageobjects.magento;

import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class ProductDetailPage extends PageObject {

    public static final By PRODUCT_NAME = By.cssSelector(".page-title span.base");
    public static final By PRICE = By.cssSelector(".product-info-price .price");
    public static final By ADD_TO_CART = By.id("product-addtocart-button");

    public String productName() {
        return new WebDriverWait(getDriver(), Duration.ofSeconds(15))
                .until(driver -> {
                    String text = driver.findElement(PRODUCT_NAME).getText().trim();
                    return text.isEmpty() ? null : text;
                });
    }

    public String price() {
        return new WebDriverWait(getDriver(), Duration.ofSeconds(15))
                .until(driver -> {
                    String text = driver.findElement(PRICE).getText().trim();
                    return text.isEmpty() ? null : text;
                });
    }

    public boolean addToCartIsAvailable() {
        return $(ADD_TO_CART).isCurrentlyVisible();
    }
}
