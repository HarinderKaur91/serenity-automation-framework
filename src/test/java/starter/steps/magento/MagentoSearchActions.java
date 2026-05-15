package starter.steps.magento;

import net.serenitybdd.annotations.Step;
import starter.pageobjects.magento.MagentoHomePage;
import starter.pageobjects.magento.ProductDetailPage;

import java.util.List;

public class MagentoSearchActions {

    MagentoHomePage homePage;
    ProductDetailPage productDetailPage;

    @Step("Open the Magento store home page")
    public void openHomePage() {
        homePage.open();
    }

    @Step("Search for {0}")
    public void searchFor(String term) {
        homePage.searchFor(term);
    }

    @Step("Read the product result names")
    public List<String> productResults() {
        return homePage.getProductResults();
    }

    @Step("Read the browser page title")
    public String pageTitle() {
        return homePage.getPageTitleText();
    }

    @Step("Open the first product in the result list")
    public void openFirstProduct() {
        homePage.openFirstProduct();
    }

    @Step("Read the product detail name")
    public String productDetailName() {
        return productDetailPage.productName();
    }

    @Step("Read the product price")
    public String productPrice() {
        return productDetailPage.price();
    }

    @Step("Check the Add to Cart button is available")
    public boolean addToCartAvailable() {
        return productDetailPage.addToCartIsAvailable();
    }
}
