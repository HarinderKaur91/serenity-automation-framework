package starter.glue.magento;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import net.serenitybdd.annotations.Steps;
import starter.steps.magento.MagentoSearchActions;

import static org.assertj.core.api.Assertions.assertThat;

public class MagentoStepDefinitions {

    @Steps
    MagentoSearchActions magentoSearchActions;

    @Given("I open the Magento store home page")
    public void openHomePage() {
        magentoSearchActions.openHomePage();
    }

    @When("I search for {string}")
    public void searchFor(String term) {
        magentoSearchActions.searchFor(term);
    }

    @Then("at least one product result should mention {string}")
    public void resultShouldMention(String term) {
        assertThat(magentoSearchActions.productResults())
                .anyMatch(text -> text.toLowerCase().contains(term.toLowerCase()));
    }

    @Then("the page title should mention {string}")
    public void pageTitleShouldMention(String term) {
        assertThat(magentoSearchActions.pageTitle()).containsIgnoringCase(term);
    }

    @When("I open the first product in the results")
    public void openFirstProduct() {
        magentoSearchActions.openFirstProduct();
    }

    @Then("the product detail page name should mention {string}")
    public void productNameShouldMention(String term) {
        assertThat(magentoSearchActions.productDetailName()).containsIgnoringCase(term);
    }

    @Then("the product price should be displayed")
    public void priceShouldBeDisplayed() {
        assertThat(magentoSearchActions.productPrice()).isNotBlank();
    }

    @Then("the Add to Cart button should be available")
    public void addToCartShouldBeAvailable() {
        assertThat(magentoSearchActions.addToCartAvailable()).isTrue();
    }
}
