package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By SEARCH_FIELD = By.cssSelector("#search, input[name='q']");
    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-name a");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");

    public void searchFor(String term) {
        $(SEARCH_FIELD).waitUntilVisible().type(term).then().sendKeys(org.openqa.selenium.Keys.ENTER);
    }

    public java.util.List<String> getProductResults() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        java.util.List<net.serenitybdd.core.pages.WebElementFacade> results = findAll(PRODUCT_RESULTS);
        if (results == null) {
            return java.util.List.of();
        }
        return results.stream()
                .map(e -> e.getDomProperty("textContent"))
                .filter(java.util.Objects::nonNull)
                .map(String::trim)
                .toList();
    }

    public void openFirstProduct() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        findAll(PRODUCT_RESULTS).get(0).click();
    }

    public String getPageTitleText() {
        if ($(PAGE_TITLE).isCurrentlyVisible()) {
            return $(PAGE_TITLE).getDomProperty("textContent").trim();
        }
        return getDriver().getTitle();
    }
}
