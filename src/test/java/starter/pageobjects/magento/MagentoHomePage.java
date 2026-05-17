package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import net.serenitybdd.core.pages.WebElementFacade;
import org.openqa.selenium.By;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By SEARCH_FIELD = By.cssSelector("input#search, input[name='q']");
    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-name a");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");

    public void searchFor(String term) {
        $(SEARCH_FIELD).waitUntilEnabled().clear();
        $(SEARCH_FIELD).typeAndEnter(term);
    }

    public java.util.List<String> getProductResults() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        java.util.List<WebElementFacade> results = findAll(PRODUCT_RESULTS);
        if (results == null) {
            return java.util.List.of();
        }
        return results.stream()
                .map(WebElementFacade::getText)
                .toList();
    }

    public void openFirstProduct() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        findAll(PRODUCT_RESULTS).get(0).click();
    }

    public String getPageTitleText() {
        String title = getDriver().getTitle();
        return title == null ? "" : title;
    }
}
