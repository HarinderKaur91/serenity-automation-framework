package starter.glue.saucedemo;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import net.serenitybdd.annotations.Steps;
import starter.steps.saucedemo.LoginActions;

import static org.assertj.core.api.Assertions.assertThat;

public class SauceDemoStepDefinitions {

    @Steps
    LoginActions loginActions;

    @Given("I open the SauceDemo login page")
    public void openLoginPage() {
        loginActions.openLoginPage();
    }

    @When("I log in as {string} with password {string}")
    public void loginAs(String username, String password) {
        loginActions.loginAs(username, password);
    }

    @Then("I should see the products inventory")
    public void shouldSeeInventory() {
        assertThat(loginActions.inventoryIsDisplayed()).isTrue();
        assertThat(loginActions.productTitles()).isNotEmpty();
    }

    @Then("I should see an error containing {string}")
    public void shouldSeeError(String expected) {
        assertThat(loginActions.errorMessage()).containsIgnoringCase(expected);
    }

    @When("I add the {string} to my cart")
    public void addProductToCart(String product) {
        loginActions.addProductToCart(product);
    }

    @Then("the cart badge should show {string}")
    public void cartBadgeShouldShow(String count) {
        assertThat(loginActions.cartBadgeCount()).isEqualTo(count);
    }

    @When("I open the shopping cart")
    public void openCart() {
        loginActions.openCart();
    }

    @Then("the cart should contain {int} item(s)")
    public void cartShouldContain(int count) {
        assertThat(loginActions.cartItemCount()).isEqualTo(count);
    }

    @When("I checkout as {string} {string} with zip {string}")
    public void checkoutAs(String firstName, String lastName, String zip) {
        loginActions.completeCheckout(firstName, lastName, zip);
    }

    @Then("I should see the order confirmation {string}")
    public void shouldSeeConfirmation(String expected) {
        assertThat(loginActions.confirmationMessage()).containsIgnoringCase(expected);
    }
}
