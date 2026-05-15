package starter.glue.herokuapp;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import net.serenitybdd.annotations.Steps;
import starter.steps.herokuapp.DynamicLoadingActions;
import starter.steps.herokuapp.HerokuAdvancedActions;

import static org.assertj.core.api.Assertions.assertThat;

public class HerokuappStepDefinitions {

    @Steps
    DynamicLoadingActions dynamicLoadingActions;

    @Steps
    HerokuAdvancedActions herokuAdvancedActions;

    @Given("I open the Heroku dynamic loading page")
    public void openPage() {
        dynamicLoadingActions.openPage();
    }

    @When("I click the Start button")
    public void clickStart() {
        dynamicLoadingActions.clickStart();
    }

    @Then("I should see the loaded text {string}")
    public void shouldSeeLoadedText(String expected) {
        assertThat(dynamicLoadingActions.loadedText()).isEqualTo(expected);
    }

    @Given("I open the Heroku file upload page")
    public void openFileUploadPage() {
        herokuAdvancedActions.openFileUploadPage();
    }

    @When("I upload a file named {string}")
    public void uploadFile(String fileName) throws Exception {
        herokuAdvancedActions.uploadTempFile(fileName);
    }

    @Then("the uploaded file name should contain {string}")
    public void uploadedNameShouldContain(String expected) {
        assertThat(herokuAdvancedActions.uploadedFileName()).contains(expected);
    }

    @Given("I open the Heroku dropdown page")
    public void openDropdownPage() {
        herokuAdvancedActions.openDropdownPage();
    }

    @When("I select dropdown option {string}")
    public void selectDropdownOption(String text) {
        herokuAdvancedActions.selectDropdownOption(text);
    }

    @Then("the selected dropdown option should be {string}")
    public void selectedDropdownShouldBe(String expected) {
        assertThat(herokuAdvancedActions.selectedDropdownOption()).isEqualTo(expected);
    }
}
