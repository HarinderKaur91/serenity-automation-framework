package starter.pageobjects.herokuapp;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://the-internet.herokuapp.com/dynamic_loading/2")
public class DynamicLoadingPage extends PageObject {

    public static final By START_BUTTON = By.cssSelector("#start button");
    public static final By LOADED_TEXT = By.cssSelector("#finish h4");

    public void clickStart() {
        $(START_BUTTON).click();
    }

    public String waitForLoadedText() {
        return $(LOADED_TEXT).waitUntilVisible().getText();
    }
}
