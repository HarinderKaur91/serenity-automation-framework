package starter.steps.herokuapp;

import net.serenitybdd.annotations.Step;
import starter.pageobjects.herokuapp.DynamicLoadingPage;

public class DynamicLoadingActions {

    DynamicLoadingPage dynamicLoadingPage;

    @Step("Open the Heroku dynamic loading page")
    public void openPage() {
        dynamicLoadingPage.open();
    }

    @Step("Click the Start button")
    public void clickStart() {
        dynamicLoadingPage.clickStart();
    }

    @Step("Wait for the loaded text to appear")
    public String loadedText() {
        return dynamicLoadingPage.waitForLoadedText();
    }
}
