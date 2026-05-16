package starter.pageobjects.saucedemo;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://www.saucedemo.com/")
public class LoginPage extends PageObject {

    public static final By USERNAME = By.id("user-name");
    public static final By PASSWORD = By.id("password");
    public static final By LOGIN_BUTTON = By.id("login-button");
    public static final By ERROR_MESSAGE = By.cssSelector("[data-test='error']");

    public void enterUsername(String username) {
        $(USERNAME).waitUntilEnabled().type(username);
    }

    public void enterPassword(String password) {
        $(PASSWORD).waitUntilEnabled().type(password);
    }

    public void clickLogin() {
        $(LOGIN_BUTTON).waitUntilEnabled().click();
    }

    public String getErrorMessage() {
        return $(ERROR_MESSAGE).waitUntilVisible().getDomProperty("textContent").trim();
    }
}
