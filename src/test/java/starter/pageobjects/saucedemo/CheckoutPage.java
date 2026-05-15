package starter.pageobjects.saucedemo;

import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

public class CheckoutPage extends PageObject {

    public static final By CHECKOUT_BUTTON = By.id("checkout");
    public static final By FIRST_NAME = By.id("first-name");
    public static final By LAST_NAME = By.id("last-name");
    public static final By POSTAL_CODE = By.id("postal-code");
    public static final By CONTINUE_BUTTON = By.id("continue");
    public static final By FINISH_BUTTON = By.id("finish");
    public static final By CONFIRMATION_HEADER = By.cssSelector(".complete-header");
    public static final By CART_ITEMS = By.cssSelector(".cart_item");

    public int cartItemCount() {
        return findAll(CART_ITEMS).size();
    }

    public void clickCheckout() {
        $(CHECKOUT_BUTTON).click();
    }

    public void fillCustomerInfo(String firstName, String lastName, String postalCode) {
        $(FIRST_NAME).type(firstName);
        $(LAST_NAME).type(lastName);
        $(POSTAL_CODE).type(postalCode);
        $(CONTINUE_BUTTON).click();
    }

    public void finishCheckout() {
        $(FINISH_BUTTON).click();
    }

    public String confirmationMessage() {
        return $(CONFIRMATION_HEADER).waitUntilVisible().getText();
    }
}
