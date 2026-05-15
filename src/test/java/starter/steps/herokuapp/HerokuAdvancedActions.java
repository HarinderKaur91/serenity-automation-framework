package starter.steps.herokuapp;

import net.serenitybdd.annotations.Step;
import starter.pageobjects.herokuapp.DropdownPage;
import starter.pageobjects.herokuapp.FileUploadPage;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class HerokuAdvancedActions {

    FileUploadPage fileUploadPage;
    DropdownPage dropdownPage;

    @Step("Open the file upload page")
    public void openFileUploadPage() {
        fileUploadPage.open();
    }

    @Step("Upload a temporary file named {0}")
    public void uploadTempFile(String fileName) throws IOException {
        Path tempFile = Files.createTempFile("upload-", "-" + fileName);
        Files.writeString(tempFile, "self-healing-framework upload payload");
        fileUploadPage.selectFile(tempFile.toAbsolutePath().toString());
        fileUploadPage.submit();
    }

    @Step("Read the name of the uploaded file shown by the server")
    public String uploadedFileName() {
        return fileUploadPage.uploadedFileName();
    }

    @Step("Open the dropdown page")
    public void openDropdownPage() {
        dropdownPage.open();
    }

    @Step("Select dropdown option {0}")
    public void selectDropdownOption(String text) {
        dropdownPage.selectByVisibleText(text);
    }

    @Step("Read the selected dropdown option")
    public String selectedDropdownOption() {
        return dropdownPage.selectedOption();
    }
}
